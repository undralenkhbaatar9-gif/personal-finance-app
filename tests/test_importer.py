from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import func, select

from finance.importer import DuplicateFileError, ValidationError, import_statement
from finance.models import Import, Transaction
from tests.conftest import build_khan_xlsx


def test_import_adds_rows_and_detects_duplicate_file(tmp_path, db_session):
    path = build_khan_xlsx(tmp_path / "statement.xlsx")

    result = import_statement(path, path.name, "khan", db_session)

    assert (result.rows_read, result.rows_new, result.rows_duplicate) == (5, 5, 0)
    with pytest.raises(DuplicateFileError):
        import_statement(path, path.name, "khan", db_session)
    assert db_session.scalar(select(func.count()).select_from(Transaction)) == 5


def test_import_counts_transaction_fingerprint_duplicates(tmp_path, db_session):
    first_path = build_khan_xlsx(tmp_path / "first.xlsx")
    import_statement(first_path, first_path.name, "khan", db_session)

    rows = [
        {
            "txn_datetime": datetime(2026, 8, 14, 9),
            "branch_code": "1000",
            "balance_before": Decimal("1000000.00"),
            "credit": Decimal("150000.00"),
            "debit": Decimal("0.00"),
            "balance_after": Decimal("1150000.00"),
            "description": "Repeated credit",
            "counterparty_account": "1234567890",
        },
        {
            "txn_datetime": datetime(2026, 8, 14, 10),
            "branch_code": "1000",
            "balance_before": Decimal("1150000.00"),
            "credit": Decimal("0.00"),
            "debit": Decimal("-93.76"),
            "balance_after": Decimal("1149906.24"),
            "description": "Repeated debit",
            "counterparty_account": "9876543210",
        },
        {
            "txn_datetime": datetime(2026, 8, 14, 14),
            "branch_code": "1000",
            "balance_before": Decimal("1149906.24"),
            "credit": Decimal("0.00"),
            "debit": Decimal("-10.00"),
            "balance_after": Decimal("1149896.24"),
            "description": "New row",
            "counterparty_account": "2222222222",
        },
    ]
    second_path = build_khan_xlsx(tmp_path / "second.xlsx", rows=rows)
    result = import_statement(second_path, second_path.name, "khan", db_session)

    assert result.rows_new == 1
    assert result.rows_duplicate == 2
    stored_imports = db_session.scalars(select(Import).order_by(Import.id)).all()
    assert stored_imports[-1].rows_duplicate == 2


def test_validation_error_rolls_back_all_writes(tmp_path, db_session):
    rows = [
        {
            "txn_datetime": datetime(2026, 8, 14, 9),
            "branch_code": "1000",
            "balance_before": Decimal("1000.00"),
            "credit": Decimal("0.00"),
            "debit": Decimal("-10.00"),
            "balance_after": Decimal("999.00"),
            "description": "Broken balance",
            "counterparty_account": "1234567890",
        }
    ]
    path = build_khan_xlsx(tmp_path / "invalid.xlsx", rows=rows)

    with pytest.raises(ValidationError) as error:
        import_statement(path, path.name, "khan", db_session)

    assert any("Row 3" in message for message in error.value.errors)
    assert db_session.scalar(select(func.count()).select_from(Transaction)) == 0
    assert db_session.scalar(select(func.count()).select_from(Import)) == 0