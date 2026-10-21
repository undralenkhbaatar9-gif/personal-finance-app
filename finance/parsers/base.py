from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TypeAlias

FilePath: TypeAlias = str | Path
CENT = Decimal("0.01")


@dataclass(frozen=True)
class StdTxn:
    txn_datetime: datetime
    amount: Decimal
    balance_before: Decimal | None
    balance_after: Decimal | None
    description: str
    counterparty_account: str | None
    branch_code: str | None


@dataclass(frozen=True)
class StatementInfo:
    account_no: str
    iban: str | None
    currency: str
    period_from: date | None
    period_to: date | None
    total_credit: Decimal | None
    total_debit: Decimal | None


class BankParser(ABC):
    code: str
    name: str

    @abstractmethod
    def detect(self, path: FilePath) -> bool:
        """Return whether the file matches this bank's statement format."""

    @abstractmethod
    def parse(self, path: FilePath) -> tuple[StatementInfo, list[StdTxn]]:
        """Parse a statement into normalized metadata and transactions."""


def to_decimal(value: object) -> Decimal:
    """Convert a bank cell value to a two-decimal Decimal, treating blanks as zero."""
    if value is None or value == "":
        return Decimal("0.00")
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, (int, float)):
        number = Decimal(str(value))
    else:
        cleaned = str(value).strip().replace(",", "")
        if not cleaned:
            return Decimal("0.00")
        try:
            number = Decimal(cleaned)
        except InvalidOperation as error:
            raise ValueError(f"Invalid monetary value: {value!r}") from error
    try:
        return number.quantize(CENT)
    except InvalidOperation as error:
        raise ValueError(f"Invalid monetary value: {value!r}") from error