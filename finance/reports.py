from datetime import date, datetime, time, timedelta
from decimal import Decimal

import pandas as pd
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from finance.models import Account, Category, Counterparty, Transaction

ZERO = Decimal("0.00")


def _transaction_query(
    session: Session,
    date_from: date,
    date_to: date,
    include_transfers: bool = False,
    include_unclassified: bool = False,
):
    query = (
        select(
            Transaction.id.label("id"),
            Transaction.txn_datetime.label("date"),
            Transaction.amount.label("amount"),
            Transaction.description.label("description"),
            Transaction.note.label("note"),
            Transaction.category_source.label("category_source"),
            Category.id.label("category_id"),
            Category.kind.label("kind"),
            Category.name.label("category"),
            Counterparty.display_name.label("counterparty"),
            Counterparty.match_key.label("match_key"),
            Account.nickname.label("account"),
            Account.account_no.label("account_no"),
        )
        .select_from(Transaction)
        .join(Account, Account.id == Transaction.account_id)
        .outerjoin(Category, Category.id == Transaction.category_id)
        .outerjoin(Counterparty, Counterparty.id == Transaction.counterparty_id)
        .where(
            Transaction.txn_datetime >= datetime.combine(date_from, time.min),
            Transaction.txn_datetime < datetime.combine(date_to + timedelta(days=1), time.min),
        )
    )
    reportable = Category.in_reports.is_(True)
    if include_transfers:
        reportable = or_(reportable, Category.kind == "transfer")
    else:
        reportable = and_(reportable, Category.kind != "transfer")
    if include_unclassified:
        query = query.where(or_(Category.id.is_(None), reportable))
    else:
        query = query.where(Category.id.is_not(None), reportable)
    return query.order_by(Transaction.txn_datetime)


def transactions_export(
    session: Session,
    date_from: date,
    date_to: date,
    include_transfers: bool = False,
    include_unclassified: bool = False,
) -> pd.DataFrame:
    """Return filtered transaction rows for tables and downloads."""
    rows = session.execute(
        _transaction_query(
            session, date_from, date_to, include_transfers, include_unclassified
        )
    ).mappings().all()
    return pd.DataFrame.from_records(rows)


def monthly_summary(
    session: Session,
    date_from: date,
    date_to: date,
    include_transfers: bool = False,
) -> pd.DataFrame:
    transactions = transactions_export(session, date_from, date_to, include_transfers)
    transactions = transactions[transactions["kind"].isin(["income", "expense"])]
    if transactions.empty:
        return pd.DataFrame(columns=["month", "income", "expense"])
    transactions["month"] = pd.to_datetime(transactions["date"]).dt.to_period("M").astype(str)
    grouped: dict[tuple[str, str], Decimal] = {}
    for row in transactions.itertuples(index=False):
        amount = row.amount if row.kind == "income" else abs(row.amount)
        key = (row.month, row.kind)
        grouped[key] = grouped.get(key, ZERO) + amount
    months = sorted({month for month, _ in grouped})
    return pd.DataFrame(
        [
            {
                "month": month,
                "income": grouped.get((month, "income"), ZERO),
                "expense": grouped.get((month, "expense"), ZERO),
            }
            for month in months
        ]
    )


def expense_by_category(
    session: Session,
    date_from: date,
    date_to: date,
    include_transfers: bool = False,
) -> pd.DataFrame:
    transactions = transactions_export(session, date_from, date_to, include_transfers)
    transactions = transactions[transactions["kind"] == "expense"]
    totals: dict[str, Decimal] = {}
    for row in transactions.itertuples(index=False):
        totals[row.category] = totals.get(row.category, ZERO) + abs(row.amount)
    return pd.DataFrame(
        sorted(
            ({"category": name, "amount": amount} for name, amount in totals.items()),
            key=lambda row: row["amount"],
            reverse=True,
        ),
        columns=["category", "amount"],
    )


def income_by_category(
    session: Session,
    date_from: date,
    date_to: date,
    include_transfers: bool = False,
) -> pd.DataFrame:
    transactions = transactions_export(session, date_from, date_to, include_transfers)
    transactions = transactions[transactions["kind"] == "income"]
    totals: dict[str, Decimal] = {}
    for row in transactions.itertuples(index=False):
        totals[row.category] = totals.get(row.category, ZERO) + row.amount
    return pd.DataFrame(
        sorted(
            ({"category": name, "amount": amount} for name, amount in totals.items()),
            key=lambda row: row["amount"],
            reverse=True,
        ),
        columns=["category", "amount"],
    )


def top_counterparties(
    session: Session,
    date_from: date,
    date_to: date,
    include_transfers: bool = False,
    n: int = 10,
) -> pd.DataFrame:
    transactions = transactions_export(session, date_from, date_to, include_transfers)
    totals: dict[str, Decimal] = {}
    for row in transactions.itertuples(index=False):
        label = row.counterparty or row.match_key or "Unknown"
        totals[label] = totals.get(label, ZERO) + abs(row.amount)
    return pd.DataFrame(
        sorted(
            ({"counterparty": name, "amount": amount} for name, amount in totals.items()),
            key=lambda row: row["amount"],
            reverse=True,
        )[:n],
        columns=["counterparty", "amount"],
    )


def unclassified_total(session: Session, date_from: date, date_to: date) -> Decimal:
    amount = session.scalar(
        select(func.sum(func.abs(Transaction.amount))).where(
            Transaction.category_id.is_(None),
            Transaction.txn_datetime >= datetime.combine(date_from, time.min),
            Transaction.txn_datetime < datetime.combine(date_to + timedelta(days=1), time.min),
        )
    )
    return amount or ZERO