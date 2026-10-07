from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from business_master.domain.clock import utcnow

_AMOUNT_QUANTUM = Decimal("0.000001")
_MAX_AMOUNT = Decimal("999999999999999999.999999")


class LedgerSide(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class LedgerAccount(StrEnum):
    CASH = "cash"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    ACCOUNTS_PAYABLE = "accounts_payable"
    WORKING_CAPITAL_ASSET = "working_capital_asset"
    REVENUE = "revenue"
    REFUNDS_RETURNS = "refunds_returns"
    FEES = "fees"
    DIRECT_COSTS = "direct_costs"
    ACQUISITION_SPEND = "acquisition_spend"
    EQUITY = "equity"


class LedgerPosting(BaseModel):
    account: LedgerAccount
    side: LedgerSide
    amount: Decimal
    currency: str = Field(min_length=3, max_length=3)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, amount: Decimal) -> Decimal:
        if not amount.is_finite():
            raise ValueError("ledger amount must be finite")
        if amount <= 0:
            raise ValueError("ledger amount must be positive")
        if amount > _MAX_AMOUNT:
            raise ValueError("ledger amount exceeds numeric(24,6) capacity")
        if amount.quantize(_AMOUNT_QUANTUM) != amount:
            raise ValueError("ledger amount supports at most 6 decimal places")
        return amount

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, currency: str) -> str:
        normalized = currency.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("currency must be a 3-letter alphabetic code")
        return normalized


class LedgerTransactionRequest(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=255)
    occurred_at: datetime
    description: str = Field(min_length=1, max_length=500)
    postings: tuple[LedgerPosting, ...]
    experiment_id: UUID | None = None
    offer_id: UUID | None = None
    channel_id: UUID | None = None
    external_ref: str | None = Field(default=None, max_length=255)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("idempotency_key", "description")
    @classmethod
    def validate_trimmed(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("ledger identifiers and descriptions must be trimmed")
        return value

    @field_validator("external_ref")
    @classmethod
    def validate_optional_trimmed(cls, value: str | None) -> str | None:
        if value is not None and value != value.strip():
            raise ValueError("external_ref must be trimmed")
        return value

    @field_validator("occurred_at")
    @classmethod
    def validate_occurred_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
        return value

    @model_validator(mode="after")
    def validate_double_entry(self) -> Self:
        if len(self.postings) < 2:
            raise ValueError("ledger transaction requires at least two postings")

        currencies = {posting.currency for posting in self.postings}
        if len(currencies) != 1:
            raise ValueError("ledger transaction cannot mix currencies")

        debits = sum(
            (posting.amount for posting in self.postings if posting.side is LedgerSide.DEBIT),
            start=Decimal(0),
        )
        credits = sum(
            (posting.amount for posting in self.postings if posting.side is LedgerSide.CREDIT),
            start=Decimal(0),
        )
        if debits != credits:
            raise ValueError("ledger transaction must balance exactly")
        return self

    @property
    def currency(self) -> str:
        return self.postings[0].currency


class LedgerTransaction(LedgerTransactionRequest):
    id: UUID = Field(default_factory=uuid4)
    recorded_at: datetime = Field(default_factory=utcnow)


class EconomicLedgerSnapshot(BaseModel):
    currency: str
    cash_available: Decimal = Decimal(0)
    receivables: Decimal = Decimal(0)
    payables: Decimal = Decimal(0)
    working_capital_assets: Decimal = Decimal(0)
    working_capital_exposure: Decimal = Decimal(0)
    recognized_revenue: Decimal = Decimal(0)
    refunds_returns: Decimal = Decimal(0)
    fees: Decimal = Decimal(0)
    direct_costs: Decimal = Decimal(0)
    acquisition_spend: Decimal = Decimal(0)
    contribution_margin: Decimal = Decimal(0)
    contribution_after_acquisition: Decimal = Decimal(0)
