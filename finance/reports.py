from datetime import date, datetime, time, timedelta
from decimal import Decimal
import traceback

import pandas as pd
from sqlalchemy import text
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
    # Хүснэгтийн багануудыг динамикаар шалгах
    tx_cols = [row[1] for row in session.execute(text("PRAGMA table_info(transactions)")).fetchall()]
    cat_cols = [row[1] for row in session.execute(text("PRAGMA table_info(categories)")).fetchall()]
    
    date_col = next((c for c in ["txn_datetime", "date", "transaction_date"] if c in tx_cols), "txn_datetime")
    
    query_sql = f"""
        SELECT 
            t.id AS id,
            t.{date_col} AS date,
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
        WHERE t.{date_col} >= :dt_from AND t.{date_col} < :dt_to
    """
    
    params = {
        "dt_from": datetime.combine(date_from, time.min),
        "dt_to": datetime.combine(date_to + timedelta(days=1), time.min)
    }
    
    return query_sql, params


def transactions_export(
    session: Session,
    date_from: date,
    date_to: date,
    include_transfers: bool = False,
    include_unclassified: bool = False,
) -> pd.DataFrame:
    """Return filtered transaction rows for tables and downloads safely."""
    try:
        sql, params = _transaction_query(session, date_from, date_to, include_transfers, include_unclassified)
        rows = session.execute(text(sql), params).mappings().all()
        
        df = pd.DataFrame.from_records(rows)
        if df.empty:
            return pd.DataFrame(columns=[
                "id", "date", "amount", "description", "note", "category_source",
                "category_id", "kind", "category", "counterparty", "match_key", "account", "account_no"
            ])
            
        # Filter transfers and unclassified based on parameters
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
        tx_cols = [row[1] for row in session.execute(text("PRAGMA table_info(transactions)")).fetchall()]
        date_col = next((c for c in ["txn_datetime", "date", "transaction_date"] if c in tx_cols), "txn_datetime")
        
        query = text(f"""
            SELECT SUM(ABS(amount)) FROM transactions 
            WHERE category_id IS NULL 
            AND {date_col} >= :dt_from AND {date_col} < :dt_to
        """)
        amount = session.scalar(query, {
            "dt_from": datetime.combine(date_from, time.min),
            "dt_to": datetime.combine(date_to + timedelta(days=1), time.min)
        })
        return Decimal(str(amount)) if amount is not None else ZERO
    except Exception as e:
        print(f"Error in unclassified_total: {e}")
        return ZERO