from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from finance.models import Account, Bank, Base, Budget, Category, Counterparty, Rule, Transaction
from finance.classifier import classify_transactions, match_rule, test_rule as preview_rule


def test_budget_model_is_exported_and_registered():
    assert Budget.__tablename__ == "budgets"
    assert Base.metadata.tables["budgets"] is Budget.__table__


def _base_rows(session: Session):
    bank = session.scalar(select(Bank).where(Bank.code == "khan"))
    account_a = Account(bank_id=bank.id, account_no="111", is_own=True)
    account_b = Account(bank_id=bank.id, account_no="222", is_own=True)
    session.add_all([account_a, account_b])
    income = session.scalar(
        select(Category).where(Category.kind == "income", Category.name == "Self-earned")
    )
    expense = session.scalar(
        select(Category).where(Category.kind == "expense", Category.name == "Groceries")
    )
    transfer = session.scalar(
        select(Category).where(
            Category.kind == "transfer", Category.name == "Between own accounts"
        )
    )
    session.flush()
    return account_a, account_b, income, expense, transfer


def _txn(txn_id: int, account_id: int, amount: str, when: datetime, **values):
    return Transaction(
        id=txn_id,
        account_id=account_id,
        txn_datetime=when,
        amount=Decimal(amount),
        balance_before=Decimal("1000.00"),
        balance_after=Decimal("1000.00") + Decimal(amount),
        description=values.get("description", "Payment"),
        counterparty_account=values.get("counterparty_account"),
        branch_code=values.get("branch_code"),
        counterparty_id=values.get("counterparty_id"),
        category_id=values.get("category_id"),
        category_source=values.get("category_source", "unclassified"),
        fingerprint=f"fingerprint-{txn_id}",
    )


def test_manual_category_is_never_changed(db_session):
    account_a, _, _, expense, _ = _base_rows(db_session)
    db_session.add(_txn(1, account_a.id, "-10", datetime(2026, 1, 1), category_id=expense.id, category_source="manual"))
    db_session.flush()

    classify_transactions(db_session)

    txn = db_session.get(Transaction, 1)
    assert txn.category_id == expense.id
    assert txn.category_source == "manual"


def test_counterparty_default_and_ask_per_txn(db_session):
    account_a, _, income, expense, _ = _base_rows(db_session)
    default_cp = Counterparty(match_key="acct:1", default_category_id=income.id)
    ask_cp = Counterparty(match_key="acct:2", default_category_id=income.id, ask_per_txn=True)
    db_session.add_all([default_cp, ask_cp])
    db_session.flush()
    db_session.add_all([
        _txn(1, account_a.id, "10", datetime(2026, 1, 1), counterparty_id=default_cp.id),
        _txn(2, account_a.id, "-10", datetime(2026, 1, 2), counterparty_id=ask_cp.id),
    ])
    db_session.flush()

    classify_transactions(db_session)

    assert db_session.get(Transaction, 1).category_id == income.id
    assert db_session.get(Transaction, 1).category_source == "counterparty"
    assert db_session.get(Transaction, 2).category_id is None
    assert db_session.get(Transaction, 2).category_source == "unclassified"


def test_rules_obey_priority_and_amount_sign(db_session):
    account_a, _, _, expense, _ = _base_rows(db_session)
    high_priority = Category(kind="expense", name="High priority")
    db_session.add(high_priority)
    db_session.flush()
    db_session.add_all([
        Rule(priority=10, field="description", match_type="contains", pattern="shop", category_id=high_priority.id, active=True),
        Rule(priority=20, field="description", match_type="contains", pattern="SHOP", amount_sign=-1, category_id=expense.id, active=True),
    ])
    txn = _txn(1, account_a.id, "-10", datetime(2026, 1, 1), description="Shop payment")
    db_session.add(txn)
    db_session.flush()

    classify_transactions(db_session)

    assert txn.category_id == high_priority.id
    assert txn.category_source == "rule"
    positive = _txn(2, account_a.id, "10", datetime(2026, 1, 2), description="Shop payment")
    assert not match_rule(db_session.scalar(select(Rule).where(Rule.amount_sign == -1)), positive, None)


def test_seed_rule_and_own_account_pair(db_session):
    account_a, account_b, _, _, transfer = _base_rows(db_session)
    bank_fee = db_session.scalar(
        select(Category).where(
            Category.kind == "expense", Category.name == "Bank fees & charges"
        )
    )
    db_session.add_all([
        _txn(1, account_a.id, "-25", datetime(2026, 1, 1, 10), branch_code="5000"),
        _txn(2, account_a.id, "-50", datetime(2026, 1, 1, 11)),
        _txn(3, account_b.id, "50", datetime(2026, 1, 1, 11, 5)),
    ])
    db_session.flush()

    classify_transactions(db_session)

    assert db_session.get(Transaction, 1).category_id == bank_fee.id
    assert db_session.get(Transaction, 1).category_source == "rule"
    assert db_session.get(Transaction, 2).category_id == transfer.id
    assert db_session.get(Transaction, 3).category_id == transfer.id


def test_test_rule_returns_matching_transactions(db_session):
    account_a, _, _, _, _ = _base_rows(db_session)
    db_session.add(_txn(1, account_a.id, "-5", datetime(2026, 1, 1), description="Monthly fee"))
    db_session.flush()

    result = preview_rule(db_session, {"field": "description", "match_type": "contains", "pattern": "fee"})

    assert len(result) == 1
    assert result.iloc[0]["description"] == "Monthly fee"