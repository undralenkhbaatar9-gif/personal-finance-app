from decimal import Decimal

from finance.parsers.base import to_decimal
from finance.parsers.khan import KhanParser


def test_parse_khan_statement(khan_xlsx):
    parser = KhanParser()

    assert parser.detect(khan_xlsx)
    info, transactions = parser.parse(khan_xlsx)

    assert info.account_no == "5954230716"
    assert info.iban == "MN660005005954230716"
    assert info.currency == "MNT"
    assert len(transactions) == 5
    assert transactions[0].amount == Decimal("150000.00")
    assert transactions[1].amount == Decimal("-93.76")
    assert transactions[4].branch_code == "5000"
    assert transactions[4].counterparty_account is None
    assert info.total_credit == Decimal("176000.00")
    assert info.total_debit == Decimal("6093.76")
    for previous, current in zip(transactions, transactions[1:]):
        assert previous.balance_after == current.balance_before


def test_to_decimal_normalizes_values():
    assert to_decimal("1,234.50") == Decimal("1234.50")
    assert to_decimal(-93.76) == Decimal("-93.76")
    assert to_decimal(0) == Decimal("0.00")
    assert to_decimal("") == Decimal("0.00")
    assert to_decimal(None) == Decimal("0.00")