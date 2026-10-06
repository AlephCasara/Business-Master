from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from business_master.domain.enums import (
    DecisionType,
    EvidenceTier,
    ExperimentStatus,
    ResourceKind,
    RiskLevel,
    SignalKind,
)


def utcnow() -> datetime:
    return datetime.now(UTC)


class EvidenceRef(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    kind: str
    source: str
    observed_at: datetime = Field(default_factory=utcnow)
    entity_id: UUID | None = None
    features: dict[str, float | int | str | bool | None] = Field(default_factory=dict)
    payload_ref: str | None = None


class Hypothesis(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    thesis: str
    family: str
    market: str | None = None
    audience: str | None = None
    tier: EvidenceTier = EvidenceTier.PROBE
    parent_id: UUID | None = None
    evidence_ids: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    active: bool = True


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


class BusinessOutcome(BaseModel):
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


class Resource(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    kind: ResourceKind
    available: bool = True
    capacity: float = 1.0
    labels: dict[str, str | int | float | bool] = Field(default_factory=dict)
    last_seen_at: datetime = Field(default_factory=utcnow)


class ExecutionResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    experiment_id: UUID | None = None
    success: bool
    signal_kind: SignalKind
    started_at: datetime
    completed_at: datetime = Field(default_factory=utcnow)
    wall_seconds: float = 0.0
    cpu_seconds: float | None = None
    gpu_seconds: float | None = None
    model_tokens: int | None = None
    retries: int = 0
    human_minutes: float = 0.0
    cash_cost: float = 0.0
    error_code: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class HumanActionRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    action_type: str
    reason: str
    experiment_id: UUID | None = None
    account_id: UUID | None = None
    risk: RiskLevel = RiskLevel.HIGH
    required_by: datetime | None = None
    created_at: datetime = Field(default_factory=utcnow)
    resolved_at: datetime | None = None
