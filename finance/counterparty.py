import re
from datetime import date
from typing import Pattern

from sqlalchemy import select
from sqlalchemy.orm import Session

from finance.models import Counterparty, Transaction

POS_PATTERNS: dict[str, list[str | Pattern[str]]] = {"khan": []}
MASKED_CARD_PATTERN = re.compile(r"\b\d{4}\*+\d{4}\b")
DATE_TEXT_PATTERN = re.compile(r"\b\d{4}[-/.]\d{2}[-/.]\d{2}\b")


def normalise_merchant(value: str) -> str:
    """Normalize a captured POS merchant name to a stable uppercase label."""
    value = MASKED_CARD_PATTERN.sub(" ", value)
    value = DATE_TEXT_PATTERN.sub(" ", value)
    tokens = [
        token
        for token in value.upper().split()
        if not (token.isdigit() and len(token) >= 4)
    ]
    return " ".join(tokens)


def extract_match_key(
    bank_code: str,
    description: str,
    counterparty_account: str | None,
    branch_code: str | None,
) -> str:
    """Return the first matching POS, account, or branch-based counterparty key."""
    for pattern in POS_PATTERNS.get(bank_code, []):
        compiled = re.compile(pattern, re.IGNORECASE) if isinstance(pattern, str) else pattern
        match = compiled.search(description)
        if match is not None:
            merchant = match.group(1) if match.lastindex else match.group(0)
            return f"pos:{normalise_merchant(merchant)}"

    if counterparty_account:
        account_digits = re.sub(r"\D", "", counterparty_account)
        if account_digits:
            return f"acct:{account_digits}"
    return f"system:{branch_code or 'unknown'}"


def get_or_create_counterparty(
    session: Session, match_key: str, first_seen: date
) -> Counterparty:
    counterparty = session.scalar(
        select(Counterparty).where(Counterparty.match_key == match_key)
    )
    if counterparty is None:
        counterparty = Counterparty(match_key=match_key, first_seen=first_seen)
        session.add(counterparty)
        session.flush()
    elif counterparty.first_seen is None or first_seen < counterparty.first_seen:
        counterparty.first_seen = first_seen
    return counterparty


def attach_counterparties(
    session: Session, txn_ids: list[int], bank_code: str
) -> None:
    if not txn_ids:
        return
    transactions = session.scalars(
        select(Transaction).where(Transaction.id.in_(txn_ids))
    ).all()
    for transaction in transactions:
        match_key = extract_match_key(
            bank_code,
            transaction.description or "",
            transaction.counterparty_account,
            transaction.branch_code,
        )
        counterparty = get_or_create_counterparty(
            session, match_key, transaction.txn_datetime.date()
        )
        transaction.counterparty_id = counterparty.id