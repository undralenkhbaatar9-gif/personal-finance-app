from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from finance.db import Base


class Bank(Base):
    __tablename__ = "banks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bank_id: Mapped[int | None] = mapped_column(ForeignKey("banks.id"))
    account_no: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    iban: Mapped[str | None] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(
        CHAR(3), nullable=False, server_default=text("'MNT'")
    )
    nickname: Mapped[str | None] = mapped_column(Text)
    is_own: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )


class Import(Base):
    __tablename__ = "imports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"))
    file_name: Mapped[str] = mapped_column(Text, nullable=False)
    file_sha256: Mapped[str] = mapped_column(CHAR(64), unique=True, nullable=False)
    period_from: Mapped[date | None] = mapped_column(Date)
    period_to: Mapped[date | None] = mapped_column(Date)
    rows_read: Mapped[int | None] = mapped_column(Integer)
    rows_new: Mapped[int | None] = mapped_column(Integer)
    rows_duplicate: Mapped[int | None] = mapped_column(Integer)
    imported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('income', 'expense', 'transfer')", name="ck_categories_kind"
        ),
        UniqueConstraint("kind", "name", name="uq_categories_kind_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    in_reports: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )


class Counterparty(Base):
    __tablename__ = "counterparties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(Text)
    default_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id")
    )
    is_own_account: Mapped[bool | None] = mapped_column(
        Boolean, server_default=text("false")
    )
    ask_per_txn: Mapped[bool | None] = mapped_column(
        Boolean, server_default=text("false")
    )
    first_seen: Mapped[date | None] = mapped_column(Date)


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "category_source IN ('manual', 'transfer', 'counterparty', 'rule', 'unclassified')",
            name="ck_transactions_category_source",
        ),
        UniqueConstraint(
            "account_id", "fingerprint", name="uq_transactions_account_fingerprint"
        ),
        Index("ix_transactions_txn_datetime", "txn_datetime"),
        Index("ix_transactions_category_id", "category_id"),
        Index("ix_transactions_counterparty_id", "counterparty_id"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True
    )
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    import_id: Mapped[int | None] = mapped_column(ForeignKey("imports.id"))
    txn_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2), nullable=False)
    balance_before: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    balance_after: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    description: Mapped[str | None] = mapped_column(Text)
    counterparty_account: Mapped[str | None] = mapped_column(Text)
    branch_code: Mapped[str | None] = mapped_column(Text)
    counterparty_id: Mapped[int | None] = mapped_column(
        ForeignKey("counterparties.id")
    )
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    category_source: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'unclassified'")
    )
    note: Mapped[str | None] = mapped_column(Text)
    fingerprint: Mapped[str] = mapped_column(CHAR(64), nullable=False)


class Rule(Base):
    __tablename__ = "rules"
    __table_args__ = (
        CheckConstraint(
            "field IN ('description', 'counterparty_account', 'branch_code', 'match_key')",
            name="ck_rules_field",
        ),
        CheckConstraint(
            "match_type IN ('equals', 'contains', 'regex')", name="ck_rules_match_type"
        ),
        CheckConstraint("amount_sign IN (-1, 1)", name="ck_rules_amount_sign"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("100")
    )
    field: Mapped[str] = mapped_column(Text, nullable=False)
    match_type: Mapped[str] = mapped_column(Text, nullable=False)
    pattern: Mapped[str] = mapped_column(Text, nullable=False)
    amount_sign: Mapped[int | None] = mapped_column(SmallInteger)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("true"))