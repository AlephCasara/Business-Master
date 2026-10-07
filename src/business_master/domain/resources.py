from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from business_master.domain.clock import utcnow
from business_master.domain.enums import ResourceKind, ResourceReservationStatus


class ResourceVector(BaseModel):
    """Non-fungible quantities keyed by stable resource name.

    Quantities are intentionally kept as a vector. Cash, GPU time, browser capacity,
    platform actions, and human attention must not be collapsed into one scalar budget
    before a policy explicitly prices that trade-off.
    """

    quantities: dict[str, Decimal] = Field(default_factory=dict)

    @field_validator("quantities")
    @classmethod
    def validate_quantities(cls, quantities: dict[str, Decimal]) -> dict[str, Decimal]:
        normalized: dict[str, Decimal] = {}
        for key, amount in quantities.items():
            if not key or key != key.strip():
                raise ValueError("resource keys must be non-empty and trimmed")
            if len(key) > 128:
                raise ValueError("resource keys cannot exceed 128 characters")
            if not amount.is_finite():
                raise ValueError("resource quantities must be finite")
            if amount < 0:
                raise ValueError("resource quantities cannot be negative")
            if amount != 0:
                normalized[key] = amount
        return dict(sorted(normalized.items()))

    def amount(self, resource_name: str) -> Decimal:
        return self.quantities.get(resource_name, Decimal(0))

    def fits_within(self, available: ResourceVector) -> bool:
        return all(amount <= available.amount(name) for name, amount in self.quantities.items())

    def plus(self, other: ResourceVector) -> ResourceVector:
        keys = self.quantities.keys() | other.quantities.keys()
        return ResourceVector(
            quantities={name: self.amount(name) + other.amount(name) for name in keys}
        )

    def minus(self, other: ResourceVector) -> ResourceVector:
        keys = self.quantities.keys() | other.quantities.keys()
        result = {name: self.amount(name) - other.amount(name) for name in keys}
        if any(amount < 0 for amount in result.values()):
            raise ValueError("resource vector subtraction cannot produce negative quantities")
        return ResourceVector(quantities=result)


class Resource(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=128)
    kind: ResourceKind
    available: bool = True
    capacity: Decimal = Field(default=Decimal("1"), ge=Decimal("0"))
    labels: dict[str, str | int | float | bool] = Field(default_factory=dict)
    last_seen_at: datetime = Field(default_factory=utcnow)

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        if name != name.strip():
            raise ValueError("resource name must be trimmed")
        return name

    @field_validator("capacity")
    @classmethod
    def validate_capacity(cls, capacity: Decimal) -> Decimal:
        if not capacity.is_finite():
            raise ValueError("resource capacity must be finite")
        return capacity


def _validate_aware_datetime(value: datetime | None) -> datetime | None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError("resource timestamps must be timezone-aware")
    return value


class ResourceReservationRequest(BaseModel):
    owner_type: str = Field(min_length=1, max_length=64)
    owner_id: UUID
    idempotency_key: str = Field(min_length=1, max_length=255)
    requirements: ResourceVector
    expires_at: datetime | None = None

    @field_validator("owner_type", "idempotency_key")
    @classmethod
    def validate_trimmed(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("reservation identifiers must be trimmed")
        return value

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, value: datetime | None) -> datetime | None:
        return _validate_aware_datetime(value)

    @model_validator(mode="after")
    def validate_non_empty(self) -> Self:
        if not self.requirements.quantities:
            raise ValueError("resource reservation requires at least one positive quantity")
        return self


class ResourceReservation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    owner_type: str = Field(min_length=1, max_length=64)
    owner_id: UUID
    idempotency_key: str = Field(min_length=1, max_length=255)
    requirements: ResourceVector
    status: ResourceReservationStatus = ResourceReservationStatus.ACTIVE
    created_at: datetime = Field(default_factory=utcnow)
    expires_at: datetime | None = None
    released_at: datetime | None = None
    expired_at: datetime | None = None

    @field_validator("created_at", "expires_at", "released_at", "expired_at")
    @classmethod
    def validate_timestamps(cls, value: datetime | None) -> datetime | None:
        return _validate_aware_datetime(value)

    @model_validator(mode="after")
    def validate_lifecycle(self) -> Self:
        if not self.requirements.quantities:
            raise ValueError("resource reservation requires at least one positive quantity")
        if self.status is ResourceReservationStatus.ACTIVE:
            if self.released_at is not None or self.expired_at is not None:
                raise ValueError("active reservation cannot be released or expired")
        if self.status is ResourceReservationStatus.RELEASED and self.released_at is None:
            raise ValueError("released reservation requires released_at")
        if self.expired_at is not None:
            if self.expires_at is None:
                raise ValueError("expired reservation requires expires_at")
            if self.status is not ResourceReservationStatus.RELEASED:
                raise ValueError("expired reservation must be released")
            if self.released_at != self.expired_at:
                raise ValueError("expired reservation must release at expired_at")
            if self.expired_at < self.expires_at:
                raise ValueError("expired_at cannot precede expires_at")
        return self


class ResourceUsageRequest(BaseModel):
    reservation_id: UUID
    idempotency_key: str = Field(min_length=1, max_length=255)
    actual: ResourceVector
    execution_id: UUID | None = None

    @field_validator("idempotency_key")
    @classmethod
    def validate_usage_key(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("usage idempotency key must be trimmed")
        return value

    @model_validator(mode="after")
    def validate_actual_usage(self) -> Self:
        if not self.actual.quantities:
            raise ValueError("resource usage requires at least one positive quantity")
        return self


class ResourceUsage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    reservation_id: UUID
    idempotency_key: str = Field(min_length=1, max_length=255)
    actual: ResourceVector
    execution_id: UUID | None = None
    observed_at: datetime = Field(default_factory=utcnow)

    @field_validator("observed_at")
    @classmethod
    def validate_observed_at(cls, value: datetime) -> datetime:
        validated = _validate_aware_datetime(value)
        assert validated is not None
        return validated

    @model_validator(mode="after")
    def validate_actual_usage(self) -> Self:
        if not self.actual.quantities:
            raise ValueError("resource usage requires at least one positive quantity")
        return self


class ResourceAvailability(BaseModel):
    capacity: ResourceVector
    reserved: ResourceVector
    available: ResourceVector
