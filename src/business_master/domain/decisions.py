from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from pydantic import BaseModel, Field, field_validator

from business_master.domain.capital import CapitalRequirement
from business_master.domain.clock import utcnow
from business_master.domain.enums import DecisionType, EvidenceTier, RiskLevel
from business_master.domain.experiment_contracts import ExperimentContract
from business_master.domain.experiments import Experiment
from business_master.domain.portfolio import RiskAssessment
from business_master.domain.resources import ResourceReservation, ResourceVector


class Decision(BaseModel):
    """Legacy V0 decision surface retained during the strangler migration."""

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


class ContinuationKind(StrEnum):
    NONE = "none"
    REPLICATE = "replicate"
    GRADUATE = "graduate"


class AutonomousContinuationRequest(BaseModel):
    """Minimal caller input for a PR10 continuation.

    Evidence, belief, evaluation, resource, risk, capital, and target-tier authority
    are deliberately absent. The store derives those facts from persisted state.
    """

    idempotency_key: str = Field(min_length=1, max_length=255)
    parent_experiment_id: UUID
    portfolio_allocation_id: UUID
    reservation_expires_at: datetime | None = None

    @field_validator("idempotency_key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("continuation idempotency_key must be trimmed")
        return value

    @field_validator("reservation_expires_at")
    @classmethod
    def validate_expiry(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("reservation_expires_at must be timezone-aware")
        return value


class AutonomousDecision(BaseModel):
    """Persisted V2 control-plane decision with causal and allocation lineage."""

    id: UUID
    idempotency_key: str
    parent_experiment_id: UUID
    portfolio_allocation_id: UUID
    family_evaluation_id: UUID
    hypothesis_id: UUID
    source_contract_id: UUID
    belief_state_version: int = Field(ge=1)
    decision_type: DecisionType
    continuation_kind: ContinuationKind
    target_tier: EvidenceTier | None = None
    policy_name: str = Field(min_length=1)
    policy_version: str = Field(min_length=1)
    evidence_ids: list[UUID] = Field(default_factory=list)
    observed_features: dict[str, Any] = Field(default_factory=dict)
    expected_resource_demand: ResourceVector = Field(default_factory=ResourceVector)
    capital_requirement: CapitalRequirement | None = None
    risk: RiskAssessment = Field(default_factory=RiskAssessment)
    rationale: str = Field(min_length=1)
    child_experiment_id: UUID | None = None
    child_contract_id: UUID | None = None
    resource_reservation_id: UUID | None = None
    capital_authorization_id: UUID | None = None
    created_at: datetime = Field(default_factory=utcnow)

    @classmethod
    def deterministic_id(cls, idempotency_key: str) -> UUID:
        return uuid5(NAMESPACE_URL, f"business-master/autonomous-decision/{idempotency_key}")

    @classmethod
    def deterministic_child_experiment_id(cls, decision_id: UUID) -> UUID:
        return uuid5(NAMESPACE_URL, f"business-master/decision-child/{decision_id}")

    @classmethod
    def deterministic_child_contract_id(cls, decision_id: UUID) -> UUID:
        return uuid5(NAMESPACE_URL, f"business-master/decision-contract/{decision_id}")

    @classmethod
    def deterministic_reservation_id(cls, decision_id: UUID) -> UUID:
        return uuid5(NAMESPACE_URL, f"business-master/decision-reservation/{decision_id}")


class AutonomousContinuationResult(BaseModel):
    decision: AutonomousDecision
    child_experiment: Experiment | None = None
    child_contract: ExperimentContract | None = None
    resource_reservation: ResourceReservation | None = None
