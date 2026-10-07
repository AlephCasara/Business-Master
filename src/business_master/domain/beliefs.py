from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from business_master.domain.clock import utcnow
from business_master.domain.enums import FreshnessMode


class FreshnessPolicy(BaseModel):
    mode: FreshnessMode = FreshnessMode.NONE
    ttl_seconds: int | None = Field(default=None, gt=0)
    half_life_seconds: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_parameters(self) -> Self:
        if self.mode in {FreshnessMode.TTL, FreshnessMode.LINEAR_DECAY}:
            if self.ttl_seconds is None:
                raise ValueError(f"{self.mode.value} requires ttl_seconds")
        if self.mode is FreshnessMode.EXPONENTIAL_DECAY and self.half_life_seconds is None:
            raise ValueError("exponential_decay requires half_life_seconds")
        if self.mode is FreshnessMode.NONE and (
            self.ttl_seconds is not None or self.half_life_seconds is not None
        ):
            raise ValueError("none freshness policy cannot define decay parameters")
        return self


class BeliefState(BaseModel):
    hypothesis_id: UUID
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    uncertainty: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_count: int = Field(default=0, ge=0)
    valid_from: datetime = Field(default_factory=utcnow)
    last_evidence_at: datetime | None = None
    freshness: float = Field(default=1.0, ge=0.0, le=1.0)
    state_version: int = Field(default=1, ge=1)
    updated_at: datetime = Field(default_factory=utcnow)
