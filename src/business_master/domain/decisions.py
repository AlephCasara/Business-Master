from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from business_master.domain.clock import utcnow
from business_master.domain.enums import DecisionType, RiskLevel


class Decision(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    entity_id: UUID
    decision_type: DecisionType
    policy_name: str
    policy_version: str
    evidence_ids: list[UUID] = Field(default_factory=list)
    observed_features: dict[str, Any] = Field(default_factory=dict)
    expected_value: float | None = None
    expected_cash_cost: float = 0.0
    expected_compute_units: float = 0.0
    expected_human_minutes: float = 0.0
    risk: RiskLevel = RiskLevel.LOW
    rationale: str
    created_at: datetime = Field(default_factory=utcnow)
