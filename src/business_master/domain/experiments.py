from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from business_master.domain.clock import utcnow
from business_master.domain.enums import EvidenceTier, ExperimentStatus


class MutationSpec(BaseModel):
    parent_experiment_id: UUID
    changed_dimensions: dict[str, Any]
    preserved_dimensions: list[str] = Field(default_factory=list)
    rationale: str


class Experiment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    hypothesis_id: UUID
    parent_id: UUID | None = None
    status: ExperimentStatus = ExperimentStatus.PLANNED
    tier: EvidenceTier = EvidenceTier.PROBE
    business_family: str
    channel_id: UUID | None = None
    product_id: UUID | None = None
    mutation: MutationSpec | None = None
    dimensions: dict[str, Any] = Field(default_factory=dict)
    expected_cash_cost: float = 0.0
    expected_compute_units: float = 0.0
    expected_human_minutes: float = 0.0
    created_at: datetime = Field(default_factory=utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class MetricSnapshot(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    experiment_id: UUID
    observed_at: datetime = Field(default_factory=utcnow)
    age_seconds: int = 0
    metrics: dict[str, float] = Field(default_factory=dict)
    source: str
    external: bool = True
