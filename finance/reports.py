from datetime import date, datetime, time, timedelta
from decimal import Decimal
import traceback

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

# models-оос шууд импортлохын оронд шаардлагатай холболтыг db-ээс авна
from finance.db import get_session

ZERO = Decimal("0.00")


def transactions_export(
    session: Session,
    date_from: date,
    date_to: date,
    include_transfers: bool = False,
    include_unclassified: bool = False,
) -> pd.DataFrame:
    """Return filtered transaction rows safely using raw SQL."""
    try:
        dt_from = datetime.combine(date_from, time.min)
        dt_to = datetime.combine(date_to + timedelta(days=1), time.min)

        sql = """
            SELECT 
                t.id AS id,
                t.txn_datetime AS date,
                t.amount AS amount,
                t.description AS description,
                t.note AS note,
                t.category_source AS category_source,
                cat.id AS category_id,
                cat.kind AS kind,
                cat.name AS category,
                cp.display_name AS counterparty,
                cp.match_key AS match_key,
                acc.nickname AS account,
                acc.account_no AS account_no
            FROM transactions t
            JOIN accounts acc ON acc.id = t.account_id
            LEFT JOIN categories cat ON cat.id = t.category_id
            LEFT JOIN counterparties cp ON cp.id = t.counterparty_id
            WHERE t.txn_datetime >= :dt_from AND t.txn_datetime < :dt_to
        """
        
        rows = session.execute(text(sql), {"dt_from": dt_from, "dt_to": dt_to}).mappings().all()
        df = pd.DataFrame.from_records(rows)
        
        if df.empty:
            return pd.DataFrame(columns=[
                "id", "date", "amount", "description", "note", "category_source",
                "category_id", "kind", "category", "counterparty", "match_key", "account", "account_no"
            ])
            
        if "kind" in df.columns:
            if not include_transfers:
                df = df[df["kind"] != "transfer"]
            if not include_unclassified:
                df = df[df["category_id"].notna()]
                
        return df
    except Exception as e:
        print(f"Error in transactions_export: {e}")
        traceback.print_exc()
        return pd.DataFrame(columns=[
            "id", "date", "amount", "description", "note", "category_source",
            "category_id", "kind", "category", "counterparty", "match_key", "account", "account_no"
        ])


def monthly_summary(
    session: Session,
    date_from: date,
    date_to: date,
    include_transfers: bool = False,
) -> pd.DataFrame:
    transactions = transactions_export(session, date_from, date_to, include_transfers)
    if transactions.empty or "kind" not in transactions.columns:
        return pd.DataFrame(columns=["month", "income", "expense"])
    transactions = transactions[transactions["kind"].isin(["income", "expense"])]
    if transactions.empty:
        return pd.DataFrame(columns=["month", "income", "expense"])
    
    transactions["month"] = pd.to_datetime(transactions["date"]).dt.to_period("M").astype(str)
    grouped: dict[tuple[str, str], Decimal] = {}
    for row in transactions.itertuples(index=False):
        amt = Decimal(str(row.amount)) if row.amount is not None else ZERO
        amount = amt if row.kind == "income" else abs(amt)
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
    if transactions.empty or "kind" not in transactions.columns:
        return pd.DataFrame(columns=["category", "amount"])
    transactions = transactions[transactions["kind"] == "expense"]
    totals: dict[str, Decimal] = {}
    for row in transactions.itertuples(index=False):
        cat_name = row.category if row.category else "Ангилаагүй"
        amt = Decimal(str(row.amount)) if row.amount is not None else ZERO
        totals[cat_name] = totals.get(cat_name, ZERO) + abs(amt)
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
    if transactions.empty or "kind" not in transactions.columns:
        return pd.DataFrame(columns=["category", "amount"])
    transactions = transactions[transactions["kind"] == "income"]
    totals: dict[str, Decimal] = {}
    for row in transactions.itertuples(index=False):
        cat_name = row.category if row.category else "Ангилаагүй"
        amt = Decimal(str(row.amount)) if row.amount is not None else ZERO
        totals[cat_name] = totals.get(cat_name, ZERO) + amt
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
    if transactions.empty:
        return pd.DataFrame(columns=["counterparty", "amount"])
    totals: dict[str, Decimal] = {}
    for row in transactions.itertuples(index=False):
        label = getattr(row, "counterparty", None) or getattr(row, "match_key", None) or "Unknown"
        amt = Decimal(str(row.amount)) if row.amount is not None else ZERO
        totals[label] = totals.get(label, ZERO) + abs(amt)
    return pd.DataFrame(
        sorted(
            ({"counterparty": name, "amount": amount} for name, amount in totals.items()),
            key=lambda row: row["amount"],
            reverse=True,
        )[:n],
        columns=["counterparty", "amount"],
    )


def unclassified_total(session: Session, date_from: date, date_to: date) -> Decimal:
    try:
        dt_from = datetime.combine(date_from, time.min)
        dt_to = datetime.combine(date_to + timedelta(days=1), time.min)
        
        query = text("""
            SELECT SUM(ABS(amount)) FROM transactions 
            WHERE category_id IS NULL 
            AND txn_datetime >= :dt_from AND txn_datetime < :dt_to
        """)
        amount = session.scalar(query, {"dt_from": dt_from, "dt_to": dt_to})
        return Decimal(str(amount)) if amount is not None else ZERO
    except Exception as e:
        print(f"Error in unclassified_total: {e}")
        return ZERO