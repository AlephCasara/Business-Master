from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import BaseModel, Field, field_validator, model_validator

from business_master.domain.clock import utcnow
from business_master.domain.enums import RiskLevel

_AMOUNT_QUANTUM = Decimal("0.000001")
_MAX_AMOUNT = Decimal("999999999999999999.999999")


class CapitalStage(StrEnum):
    LOCKED = "locked"
    PROBE = "probe"
    VALIDATED = "validated"
    PILOT = "pilot"
    SCALE = "scale"


class SpendCategory(StrEnum):
    PAID_ADS = "paid_ads"
    EXTERNAL_AI_API = "external_ai_api"
    CLOUD_GPU = "cloud_gpu"
    PAID_SAAS = "paid_saas"
    WORKING_CAPITAL = "working_capital"
    OTHER = "other"


class CapitalAuthorizationStatus(StrEnum):
    ACTIVE = "active"
    CONSUMED = "consumed"
    RELEASED = "released"
    EXPIRED = "expired"


def _validate_amount(amount: Decimal) -> Decimal:
    if not amount.is_finite():
        raise ValueError("capital amount must be finite")
    if amount < 0:
        raise ValueError("capital amount cannot be negative")
    if amount > _MAX_AMOUNT:
        raise ValueError("capital amount exceeds numeric(24,6) capacity")
    if amount.quantize(_AMOUNT_QUANTUM) != amount:
        raise ValueError("capital amount supports at most 6 decimal places")
    return amount


def _normalize_currency(currency: str) -> str:
    normalized = currency.strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise ValueError("currency must be a 3-letter alphabetic code")
    return normalized


def _validate_aware(value: datetime | None) -> datetime | None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError("capital timestamps must be timezone-aware")
    return value


class CapitalRequirement(BaseModel):
    amount: Decimal = Field(gt=Decimal("0"))
    currency: str = Field(min_length=3, max_length=3)
    category: SpendCategory

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, amount: Decimal) -> Decimal:
        validated = _validate_amount(amount)
        if validated == 0:
            raise ValueError("capital requirement must be positive")
        return validated

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, currency: str) -> str:
        return _normalize_currency(currency)


class CapitalEnvelope(BaseModel):
    currency: str = Field(min_length=3, max_length=3)
    stage: CapitalStage
    max_per_authorization: Decimal = Decimal(0)
    max_outstanding: Decimal = Decimal(0)
    max_risk: RiskLevel = RiskLevel.LOW
    operator_hard_ceiling: Decimal | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, currency: str) -> str:
        return _normalize_currency(currency)

    @field_validator("max_per_authorization", "max_outstanding", "operator_hard_ceiling")
    @classmethod
    def validate_amounts(cls, amount: Decimal | None) -> Decimal | None:
        return None if amount is None else _validate_amount(amount)

    @field_validator("period_start", "period_end")
    @classmethod
    def validate_period_timestamp(cls, value: datetime | None) -> datetime | None:
        return _validate_aware(value)

    @model_validator(mode="after")
    def validate_period(self) -> Self:
        if (self.period_start is None) != (self.period_end is None):
            raise ValueError("capital period_start and period_end must be provided together")
        if self.period_start is not None and self.period_end is not None:
            if self.period_end <= self.period_start:
                raise ValueError("capital period_end must be after period_start")
        if self.operator_hard_ceiling is not None and self.period_start is None:
            raise ValueError("operator_hard_ceiling requires an explicit control period")
        return self


class CapitalAuthorizationRequest(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=255)
    portfolio_allocation_id: UUID
    family_evaluation_id: UUID
    hypothesis_id: UUID
    amount: Decimal = Field(gt=Decimal("0"))
    currency: str = Field(min_length=3, max_length=3)
    category: SpendCategory
    stage: CapitalStage
    risk: RiskLevel
    requested_at: datetime = Field(default_factory=utcnow)
    expires_at: datetime | None = None

    @field_validator("idempotency_key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("capital idempotency_key must be trimmed")
        return value

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, amount: Decimal) -> Decimal:
        validated = _validate_amount(amount)
        if validated == 0:
            raise ValueError("capital authorization amount must be positive")
        return validated

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, currency: str) -> str:
        return _normalize_currency(currency)

    @field_validator("requested_at", "expires_at")
    @classmethod
    def validate_timestamp(cls, value: datetime | None) -> datetime | None:
        return _validate_aware(value)

    @model_validator(mode="after")
    def validate_expiry(self) -> Self:
        if self.expires_at is not None and self.expires_at <= self.requested_at:
            raise ValueError("capital expires_at must be after requested_at")
        return self


class CapitalAssessment(BaseModel):
    authorized: bool
    ledger_cash: Decimal
    active_outstanding: Decimal
    period_committed: Decimal
    authorizable_cash: Decimal
    rationale: str


class CapitalAuthorization(BaseModel):
    id: UUID
    idempotency_key: str
    portfolio_allocation_id: UUID
    family_evaluation_id: UUID
    hypothesis_id: UUID
    amount: Decimal
    currency: str
    category: SpendCategory
    stage: CapitalStage
    risk: RiskLevel
    policy_name: str
    policy_version: str
    envelope: CapitalEnvelope
    ledger_cash_at_authorization: Decimal
    active_outstanding_before: Decimal
    period_committed_before: Decimal
    status: CapitalAuthorizationStatus = CapitalAuthorizationStatus.ACTIVE
    rationale: str
    authorized_at: datetime
    expires_at: datetime | None = None
    consumed_at: datetime | None = None
    released_at: datetime | None = None
    expired_at: datetime | None = None
    ledger_transaction_id: UUID | None = None

    @field_validator(
        "authorized_at",
        "expires_at",
        "consumed_at",
        "released_at",
        "expired_at",
    )
    @classmethod
    def validate_timestamp(cls, value: datetime | None) -> datetime | None:
        return _validate_aware(value)

    @model_validator(mode="after")
    def validate_lifecycle(self) -> Self:
        if self.status is CapitalAuthorizationStatus.ACTIVE:
            if any(
                value is not None
                for value in (
                    self.consumed_at,
                    self.released_at,
                    self.expired_at,
                    self.ledger_transaction_id,
                )
            ):
                raise ValueError("active capital authorization cannot have terminal fields")
        elif self.status is CapitalAuthorizationStatus.CONSUMED:
            if self.consumed_at is None or self.ledger_transaction_id is None:
                raise ValueError("consumed authorization requires consumption and ledger lineage")
        elif self.status is CapitalAuthorizationStatus.RELEASED:
            if self.released_at is None or self.expired_at is not None:
                raise ValueError("released authorization requires released_at only")
        elif self.status is CapitalAuthorizationStatus.EXPIRED:
            if self.released_at is None or self.expired_at is None:
                raise ValueError("expired authorization requires released_at and expired_at")
            if self.released_at != self.expired_at:
                raise ValueError("expired authorization must release at expired_at")
        return self

    @classmethod
    def deterministic_id(cls, idempotency_key: str) -> UUID:
        return uuid5(NAMESPACE_URL, f"business-master/capital-authorization/{idempotency_key}")
