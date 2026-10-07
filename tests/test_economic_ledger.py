from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from business_master.domain.ledger import (
    LedgerAccount,
    LedgerPosting,
    LedgerSide,
    LedgerTransactionRequest,
)


def _posting(
    account: LedgerAccount,
    side: LedgerSide,
    amount: str,
    currency: str = "USD",
) -> LedgerPosting:
    return LedgerPosting(
        account=account,
        side=side,
        amount=Decimal(amount),
        currency=currency,
    )


def test_balanced_transaction_is_exact_and_currency_aware() -> None:
    transaction = LedgerTransactionRequest(
        idempotency_key="sale:one",
        occurred_at=datetime(2026, 10, 7, tzinfo=UTC),
        description="Recognize sale receivable",
        postings=(
            _posting(LedgerAccount.ACCOUNTS_RECEIVABLE, LedgerSide.DEBIT, "125.50"),
            _posting(LedgerAccount.REVENUE, LedgerSide.CREDIT, "125.50"),
        ),
    )

    assert transaction.currency == "USD"
    assert transaction.postings[0].amount == Decimal("125.50")


def test_transaction_rejects_unbalanced_or_mixed_currency_postings() -> None:
    with pytest.raises(ValidationError, match="balance exactly"):
        LedgerTransactionRequest(
            idempotency_key="bad:unbalanced",
            occurred_at=datetime(2026, 10, 7, tzinfo=UTC),
            description="Unbalanced",
            postings=(
                _posting(LedgerAccount.CASH, LedgerSide.DEBIT, "10"),
                _posting(LedgerAccount.EQUITY, LedgerSide.CREDIT, "9"),
            ),
        )

    with pytest.raises(ValidationError, match="cannot mix currencies"):
        LedgerTransactionRequest(
            idempotency_key="bad:currency",
            occurred_at=datetime(2026, 10, 7, tzinfo=UTC),
            description="Mixed currencies",
            postings=(
                _posting(LedgerAccount.CASH, LedgerSide.DEBIT, "10", "USD"),
                _posting(LedgerAccount.EQUITY, LedgerSide.CREDIT, "10", "EUR"),
            ),
        )


def test_posting_rejects_float_like_precision_and_invalid_amounts() -> None:
    with pytest.raises(ValidationError, match="at most 6 decimal places"):
        _posting(LedgerAccount.CASH, LedgerSide.DEBIT, "1.0000001")

    with pytest.raises(ValidationError, match="positive"):
        _posting(LedgerAccount.CASH, LedgerSide.DEBIT, "0")

    with pytest.raises(ValidationError, match="finite"):
        _posting(LedgerAccount.CASH, LedgerSide.DEBIT, "NaN")


def test_currency_is_normalized_and_timestamp_must_be_aware() -> None:
    posting = _posting(LedgerAccount.CASH, LedgerSide.DEBIT, "1", " usd ")
    assert posting.currency == "USD"

    with pytest.raises(ValidationError, match="timezone-aware"):
        LedgerTransactionRequest(
            idempotency_key="bad:time",
            occurred_at=datetime(2026, 10, 7),
            description="Naive time",
            postings=(
                _posting(LedgerAccount.CASH, LedgerSide.DEBIT, "1"),
                _posting(LedgerAccount.EQUITY, LedgerSide.CREDIT, "1"),
            ),
        )
