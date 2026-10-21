import hashlib
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.orm import Session

from finance.counterparty import attach_counterparties
from finance.db import get_session
from finance.models import Account, Bank, Import, Transaction
from finance.parsers import PARSERS
from finance.parsers.base import StatementInfo, StdTxn


class DuplicateFileError(Exception):
    """Raised when the exact statement file has already been imported."""


class ValidationError(Exception):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("Statement validation failed:\n" + "\n".join(errors))


@dataclass(frozen=True)
class ImportResult:
    rows_read: int
    rows_new: int
    rows_duplicate: int
    errors: list[str] = field(default_factory=list)


def validate(info: StatementInfo, txns: list[StdTxn]) -> list[str]:
    """Return all running-balance, amount, and statement-total validation errors."""
    errors: list[str] = []
    credits = Decimal("0.00")
    debits = Decimal("0.00")
    previous: StdTxn | None = None

    for index, txn in enumerate(txns, start=3):
        if txn.balance_before is None or txn.balance_after is None:
            errors.append(f"Row {index}: balance_before and balance_after are required")
        elif txn.balance_before + txn.amount != txn.balance_after:
            errors.append(
                f"Row {index}: balance_before + amount does not equal balance_after"
            )
        if previous is not None and txn.balance_before != previous.balance_after:
            errors.append(f"Row {index}: balance_before does not match the previous row")
        if txn.amount > 0:
            credits += txn.amount
        elif txn.amount < 0:
            debits += abs(txn.amount)
        previous = txn

    if info.total_credit is not None and credits != info.total_credit:
        errors.append(
            f"Statement total credit {info.total_credit} does not match rows {credits}"
        )
    if info.total_debit is not None and debits != info.total_debit:
        errors.append(
            f"Statement total debit {info.total_debit} does not match rows {debits}"
        )
    return errors


def _file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as statement_file:
        for chunk in iter(lambda: statement_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint(account_no: str, txn: StdTxn) -> str:
    content = (
        f"{account_no}|{txn.txn_datetime.isoformat()}|{txn.amount:.2f}|"
        f"{txn.balance_after:.2f}|{txn.counterparty_account or ''}"
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _import_in_session(
    session: Session, path: str | Path, file_name: str, bank_code: str
) -> ImportResult:
    file_hash = _file_sha256(path)
    if session.scalar(select(Import.id).where(Import.file_sha256 == file_hash)) is not None:
        raise DuplicateFileError(f"This statement file has already been imported: {file_name}")

    parser = PARSERS.get(bank_code)
    if parser is None:
        raise ValueError(f"Unsupported bank code: {bank_code}")
    info, txns = parser.parse(path)
    errors = validate(info, txns)
    if errors:
        raise ValidationError(errors)

    bank = session.scalar(select(Bank).where(Bank.code == bank_code))
    if bank is None:
        raise ValueError(f"Bank '{bank_code}' is not seeded in the database")
    account = session.scalar(
        select(Account).where(Account.account_no == info.account_no)
    )
    if account is None:
        account = Account(
            bank_id=bank.id,
            account_no=info.account_no,
            iban=info.iban,
            currency=info.currency,
        )
        session.add(account)
        session.flush()

    import_row = Import(
        account_id=account.id,
        file_name=file_name,
        file_sha256=file_hash,
        period_from=info.period_from,
        period_to=info.period_to,
        rows_read=len(txns),
        rows_new=0,
        rows_duplicate=0,
    )
    session.add(import_row)
    session.flush()

    rows_new = 0
    inserted_ids: list[int] = []
    dialect = session.get_bind().dialect.name
    if dialect == "sqlite":
        from sqlalchemy.dialects.sqlite import insert as dialect_insert
    else:
        dialect_insert = postgresql_insert

    for txn in txns:
        values = {
            "account_id": account.id,
            "import_id": import_row.id,
            "txn_datetime": txn.txn_datetime,
            "amount": txn.amount,
            "balance_before": txn.balance_before,
            "balance_after": txn.balance_after,
            "description": txn.description,
            "counterparty_account": txn.counterparty_account,
            "branch_code": txn.branch_code,
            "category_source": "unclassified",
            "fingerprint": _fingerprint(info.account_no, txn),
        }
        statement = (
            dialect_insert(Transaction)
            .values(**values)
            .on_conflict_do_nothing(index_elements=["account_id", "fingerprint"])
            .returning(Transaction.id)
        )
        inserted_id = session.scalar(statement)
        if inserted_id is not None:
            rows_new += 1
            inserted_ids.append(inserted_id)

    rows_duplicate = len(txns) - rows_new
    import_row.rows_new = rows_new
    import_row.rows_duplicate = rows_duplicate

    if inserted_ids:
        attach_counterparties(session, inserted_ids, bank_code)
        from finance.classifier import classify_transactions

        classify_transactions(session, inserted_ids)

    return ImportResult(
        rows_read=len(txns),
        rows_new=rows_new,
        rows_duplicate=rows_duplicate,
    )


def import_statement(
    path: str | Path,
    file_name: str,
    bank_code: str,
    session: Session | None = None,
) -> ImportResult:
    """Validate, store, and classify a statement in a single transaction."""
    if session is None:
        with get_session() as active_session:
            return _import_in_session(active_session, path, file_name, bank_code)
    with session.begin_nested():
        return _import_in_session(session, path, file_name, bank_code)