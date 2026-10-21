from datetime import date
import re

from finance.counterparty import (
    POS_PATTERNS,
    extract_match_key,
    get_or_create_counterparty,
)


def test_extract_match_key_uses_account_then_branch():
    assert extract_match_key("khan", "Transfer", "MN-123 456", "5000") == "acct:123456"
    assert extract_match_key("khan", "Fee", None, "5000") == "system:5000"
    assert extract_match_key("khan", "Fee", None, None) == "system:unknown"


def test_pos_match_normalizes_merchant():
    POS_PATTERNS["khan"] = [re.compile(r"^POS\s+(.+)", re.IGNORECASE)]
    try:
        assert (
            extract_match_key(
                "khan",
                "POS CU 25 SUKHBAATAR 2026-09-03 1234****5678",
                None,
                "5000",
            )
            == "pos:CU 25 SUKHBAATAR"
        )
    finally:
        POS_PATTERNS["khan"] = []


def test_get_or_create_counterparty_is_idempotent(db_session):
    first = get_or_create_counterparty(db_session, "acct:123", date(2026, 1, 2))
    second = get_or_create_counterparty(db_session, "acct:123", date(2026, 1, 1))
    assert first.id == second.id
    assert second.first_seen.isoformat() == "2026-01-01"