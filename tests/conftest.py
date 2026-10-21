from datetime import datetime
from decimal import Decimal
import os
from pathlib import Path

import pytest
from openpyxl import Workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from finance.db import Base
from finance import models
from finance.seed import seed


def _default_rows() -> list[dict[str, object]]:
    balances = [
        (Decimal("1000000.00"), Decimal("150000.00"), Decimal("0.00")),
        (Decimal("1150000.00"), Decimal("0.00"), Decimal("-93.76")),
        (Decimal("1149906.24"), Decimal("25000.00"), Decimal("0.00")),
        (Decimal("1174906.24"), Decimal("0.00"), Decimal("-6000.00")),
        (Decimal("1168906.24"), Decimal("1000.00"), Decimal("0.00")),
    ]
    descriptions = ["Salary", "Coffee", "Transfer received", "Groceries", "Branch fee"]
    accounts = ["1234567890", "9876543210", "1234567890", "9876543210", ""]
    rows: list[dict[str, object]] = []
    for index, (before, credit, debit) in enumerate(balances):
        rows.append(
            {
                "txn_datetime": datetime(2026, 8, 14, 9 + index, 0, 0),
                "branch_code": "5000" if index == 4 else "1000",
                "balance_before": before,
                "credit": credit,
                "debit": debit,
                "balance_after": before + credit + debit,
                "description": descriptions[index],
                "counterparty_account": accounts[index],
            }
        )
    return rows


def build_khan_xlsx(
    path: str | Path, rows: list[dict[str, object]] | None = None
) -> Path:
    """Build a synthetic Khan statement workbook for parser and importer tests."""
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Statement"
    worksheet.append(
        [
            "IBAN: MN660005005954230716",
            "2026/08/14",
            "2026/10/14",
            "MNT",
        ]
    )
    worksheet.append(["Огноо", "Салбар", "Эхний үлдэгдэл", "Орлого", "Зарлага", "Эцсийн үлдэгдэл", "Гүйлгээний утга", "Харилцагч"])

    data_rows = rows if rows is not None else _default_rows()
    total_credit = Decimal("0.00")
    total_debit = Decimal("0.00")
    for row in data_rows:
        credit = Decimal(str(row["credit"]))
        debit = Decimal(str(row["debit"]))
        total_credit += credit
        total_debit += abs(debit)
        worksheet.append(
            [
                row["txn_datetime"],
                row.get("branch_code"),
                row.get("balance_before"),
                credit,
                debit,
                row.get("balance_after"),
                row.get("description"),
                row.get("counterparty_account"),
            ]
        )
    worksheet.append([None])
    worksheet.append(["Нийт", None, None, total_credit, total_debit])
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output)
    return output


@pytest.fixture
def khan_xlsx(tmp_path: Path) -> Path:
    return build_khan_xlsx(tmp_path / "khan_statement.xlsx")


@pytest.fixture
def db_session():
    database_url = os.getenv("TEST_DATABASE_URL", "sqlite://")
    engine = create_engine(database_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            seed(session)
            session.commit()
            yield session
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()