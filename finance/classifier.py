import re
from datetime import timedelta
from decimal import Decimal
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from finance.models import Account, Category, Counterparty, Rule, Transaction

TRANSFER_CATEGORY = "Between own accounts"


def _rule_value(rule: Rule | dict[str, Any], key: str, default: Any = None) -> Any:
    if isinstance(rule, dict):
        return rule.get(key, default)
    return getattr(rule, key, default)


def match_rule(rule: Rule | dict[str, Any], txn: Transaction, match_key: str | None) -> bool:
    field = _rule_value(rule, "field")
    match_type = _rule_value(rule, "match_type")
    pattern = str(_rule_value(rule, "pattern", ""))
    amount_sign = _rule_value(rule, "amount_sign")
    values = {
        "description": txn.description or "",
        "counterparty_account": txn.counterparty_account or "",
        "branch_code": txn.branch_code or "",
        "match_key": match_key or "",
    }
    value = values.get(field, "")

    if amount_sign is not None:
        actual_sign = 1 if txn.amount > 0 else -1 if txn.amount < 0 else 0
        if actual_sign != int(amount_sign):
            return False

    if match_type == "equals":
        return value.casefold() == pattern.casefold()
    if match_type == "contains":
        return pattern.casefold() in value.casefold()
    if match_type == "regex":
        try:
            return re.search(pattern, value, flags=re.IGNORECASE) is not None
        except re.error:
            return False
    return False


def _counterparty_map(
    session: Session, transactions: list[Transaction]
) -> dict[int, Counterparty]:
    ids = {txn.counterparty_id for txn in transactions if txn.counterparty_id is not None}
    if not ids:
        return {}
    return {
        counterparty.id: counterparty
        for counterparty in session.scalars(
            select(Counterparty).where(Counterparty.id.in_(ids))
        )
    }


def _transfer_pairs(
    targets: list[Transaction], candidates: list[Transaction], own_account_ids: set[int]
) -> set[int]:
    by_amount_and_sign: dict[tuple[Decimal, int], list[Transaction]] = {}
    for txn in candidates:
        if txn.account_id not in own_account_ids or txn.amount == 0:
            continue
        sign = 1 if txn.amount > 0 else -1
        key = (abs(txn.amount), sign)
        by_amount_and_sign.setdefault(key, []).append(txn)

    paired_ids: set[int] = set()
    for txn in targets:
        if txn.account_id not in own_account_ids or txn.amount == 0:
            continue
        opposite_sign = -1 if txn.amount > 0 else 1
        matches = by_amount_and_sign.get((abs(txn.amount), opposite_sign), [])
        for other in matches:
            if other.id == txn.id or other.account_id == txn.account_id:
                continue
            if abs(other.txn_datetime - txn.txn_datetime) <= timedelta(minutes=10):
                paired_ids.update((txn.id, other.id))
    return paired_ids


def classify_transactions(
    session: Session, txn_ids: list[int] | None = None
) -> None:
    query = select(Transaction).where(Transaction.category_source != "manual")
    if txn_ids is not None:
        if not txn_ids:
            return
        query = query.where(Transaction.id.in_(txn_ids))
    targets = list(session.scalars(query).all())
    if not targets:
        return

    own_accounts = session.scalars(select(Account).where(Account.is_own.is_(True))).all()
    own_account_ids = {account.id for account in own_accounts}
    own_account_numbers = {account.account_no for account in own_accounts}

    if txn_ids is None:
        candidates = session.scalars(
            select(Transaction).where(Transaction.category_source != "manual")
        ).all()
    else:
        start = min(txn.txn_datetime for txn in targets) - timedelta(minutes=10)
        end = max(txn.txn_datetime for txn in targets) + timedelta(minutes=10)
        candidates = session.scalars(
            select(Transaction).where(
                Transaction.account_id.in_(own_account_ids or {-1}),
                Transaction.txn_datetime >= start,
                Transaction.txn_datetime <= end,
                Transaction.category_source != "manual",
            )
        ).all()
    paired_ids = _transfer_pairs(targets, candidates, own_account_ids)

    rows_by_id = {txn.id: txn for txn in targets}
    if paired_ids:
        paired_rows = session.scalars(
            select(Transaction).where(Transaction.id.in_(paired_ids))
        ).all()
        rows_by_id.update({txn.id: txn for txn in paired_rows})
    rows = [txn for txn in rows_by_id.values() if txn.category_source != "manual"]

    counterparties = _counterparty_map(session, rows)
    rules = session.scalars(
        select(Rule).where(Rule.active.is_(True)).order_by(Rule.priority, Rule.id)
    ).all()
    transfer_category = session.scalar(
        select(Category).where(
            Category.kind == "transfer", Category.name == TRANSFER_CATEGORY
        )
    )
    if transfer_category is None:
        raise ValueError("Transfer category is missing; initialize and seed the database")

    for txn in rows:
        counterparty = counterparties.get(txn.counterparty_id)
        is_direct_transfer = bool(counterparty and counterparty.is_own_account)
        is_account_transfer = txn.counterparty_account in own_account_numbers
        if is_direct_transfer or is_account_transfer or txn.id in paired_ids:
            txn.category_id = transfer_category.id
            txn.category_source = "transfer"
            continue

        if counterparty and counterparty.default_category_id and not counterparty.ask_per_txn:
            txn.category_id = counterparty.default_category_id
            txn.category_source = "counterparty"
            continue

        match_key = counterparty.match_key if counterparty else None
        matched_rule = next(
            (rule for rule in rules if match_rule(rule, txn, match_key)), None
        )
        if matched_rule is not None:
            txn.category_id = matched_rule.category_id
            txn.category_source = "rule"
        else:
            txn.category_id = None
            txn.category_source = "unclassified"


def test_rule(session: Session, rule_dict: dict[str, Any]) -> pd.DataFrame:
    transactions = session.scalars(
        select(Transaction).order_by(Transaction.txn_datetime.desc()).limit(500)
    ).all()
    counterparties = _counterparty_map(session, transactions)
    categories = {
        category.id: f"{category.kind}: {category.name}"
        for category in session.scalars(select(Category))
    }
    matched = []
    for txn in transactions:
        counterparty = counterparties.get(txn.counterparty_id)
        match_key = counterparty.match_key if counterparty else None
        if match_rule(rule_dict, txn, match_key):
            matched.append(
                {
                    "date": txn.txn_datetime,
                    "amount": txn.amount,
                    "description": txn.description,
                    "counterparty_account": txn.counterparty_account,
                    "current category": categories.get(txn.category_id),
                }
            )
    return pd.DataFrame(
        matched,
        columns=["date", "amount", "description", "counterparty_account", "current category"],
    )