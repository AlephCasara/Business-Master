from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from business_master.domain.clock import utcnow


class BusinessOutcome(BaseModel):
    """Legacy-compatible outcome summary; the economic ledger is financial authority."""

    id: UUID = Field(default_factory=uuid4)
    experiment_id: UUID
    observed_at: datetime = Field(default_factory=utcnow)
    revenue: float = 0.0
    gross_profit: float | None = None
    currency: str = "USD"
    orders: int = 0
    leads: int = 0
    clicks: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class OpportunityScore(BaseModel):
    entity_id: UUID
    expected_value: float
    uncertainty: float = Field(ge=0.0)
    information_gain: float = Field(ge=0.0)
    feedback_speed: float = Field(ge=0.0)
    downstream_reuse: float = Field(ge=0.0)
    compute_cost: float = Field(ge=0.0)
    cash_cost: float = Field(ge=0.0)
    human_time_cost: float = Field(ge=0.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
