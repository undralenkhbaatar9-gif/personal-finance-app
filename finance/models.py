from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

import os
import sqlite3

from finance.db import Base

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "finance.db")


def get_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_file = os.path.join(base_dir, "..", "finance.db")
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception:
        conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn


__all__ = [
    "Base",
    "Bank",
    "Account",
    "Import",
    "Category",
    "Counterparty",
    "Transaction",
    "Rule",
    "Budget",
    "get_connection",
    "DB_PATH",
]


class Bank(Base):
    __tablename__ = "banks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    accounts: Mapped[list["Account"]] = relationship(back_populates="bank")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bank_id: Mapped[int] = mapped_column(ForeignKey("banks.id"), nullable=False)
    account_no: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    iban: Mapped[Optional[str]] = mapped_column(String)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="MNT")
    nickname: Mapped[Optional[str]] = mapped_column(String)
    is_own: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    bank: Mapped[Bank] = relationship(back_populates="accounts")
    imports: Mapped[list["Import"]] = relationship(back_populates="account")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account")


class Import(Base):
    __tablename__ = "imports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    file_sha256: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    period_from: Mapped[Optional[date]] = mapped_column(Date)
    period_to: Mapped[Optional[date]] = mapped_column(Date)
    rows_read: Mapped[Optional[int]] = mapped_column(Integer)
    rows_new: Mapped[Optional[int]] = mapped_column(Integer)
    rows_duplicate: Mapped[Optional[int]] = mapped_column(Integer)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    account: Mapped[Account] = relationship(back_populates="imports")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="import_")


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("kind", "name", name="uq_category_kind_name"),
        CheckConstraint("kind IN ('income','expense','transfer')", name="ck_category_kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    in_reports: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    parent: Mapped[Optional["Category"]] = relationship(remote_side=[id])
    rules: Mapped[list["Rule"]] = relationship(back_populates="category")
    counterparties_default: Mapped[list["Counterparty"]] = relationship(
        back_populates="default_category"
    )


class Counterparty(Base):
    __tablename__ = "counterparties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String)
    default_category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id")
    )
    is_own_account: Mapped[bool] = mapped_column(Boolean, default=False)
    ask_per_txn: Mapped[bool] = mapped_column(Boolean, default=False)
    first_seen: Mapped[Optional[date]] = mapped_column(Date)

    default_category: Mapped[Optional[Category]] = relationship(
        back_populates="counterparties_default"
    )
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="counterparty")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint("account_id", "fingerprint", name="uq_transaction_account_fingerprint"),
        CheckConstraint(
            "category_source IN ('manual','transfer','counterparty','rule','unclassified')",
            name="ck_transaction_category_source",
        ),
        Index("ix_transactions_txn_datetime", "txn_datetime"),
        Index("ix_transactions_category_id", "category_id"),
        Index("ix_transactions_counterparty_id", "counterparty_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    import_id: Mapped[Optional[int]] = mapped_column(ForeignKey("imports.id"))
    txn_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2), nullable=False)
    balance_before: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 2))
    balance_after: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 2))
    description: Mapped[Optional[str]] = mapped_column(Text)
    counterparty_account: Mapped[Optional[str]] = mapped_column(String)
    branch_code: Mapped[Optional[str]] = mapped_column(String)
    counterparty_id: Mapped[Optional[int]] = mapped_column(ForeignKey("counterparties.id"))
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    category_source: Mapped[str] = mapped_column(String, nullable=False, default="unclassified")
    note: Mapped[Optional[str]] = mapped_column(Text)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)

    account: Mapped[Account] = relationship(back_populates="transactions")
    import_: Mapped[Optional[Import]] = relationship(back_populates="transactions")
    counterparty: Mapped[Optional[Counterparty]] = relationship(back_populates="transactions")
    category: Mapped[Optional[Category]] = relationship()


class Rule(Base):
    __tablename__ = "rules"
    __table_args__ = (
        CheckConstraint(
            "field IN ('description','counterparty_account','branch_code','match_key')",
            name="ck_rule_field",
        ),
        CheckConstraint(
            "match_type IN ('equals','contains','regex')",
            name="ck_rule_match_type",
        ),
        CheckConstraint("amount_sign IS NULL OR amount_sign IN (-1,1)", name="ck_rule_amount_sign"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    field: Mapped[str] = mapped_column(String, nullable=False)
    match_type: Mapped[str] = mapped_column(String, nullable=False)
    pattern: Mapped[str] = mapped_column(String, nullable=False)
    amount_sign: Mapped[Optional[int]] = mapped_column(SmallInteger)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped[Category] = relationship(back_populates="rules")


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint("category_id", name="uq_budget_category_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    monthly_limit: Mapped[Decimal] = mapped_column(Numeric(16, 2), nullable=False)

    category: Mapped[Category] = relationship()


# Goal model removed from active use; can be added later if needed.