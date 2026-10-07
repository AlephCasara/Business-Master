from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from pydantic import BaseModel, Field, field_validator, model_validator

from business_master.domain.capital import CapitalRequirement
from business_master.domain.clock import utcnow
from business_master.domain.enums import EvidenceTier, RiskLevel
from business_master.domain.experiment_contracts import ExperimentContract
from business_master.domain.family_evaluation import (
    EvaluationRecommendation,
    FamilyEvaluation,
)
from business_master.domain.resources import ResourceAvailability, ResourceVector


class PortfolioRole(StrEnum):
    SIGNAL = "signal"
    CASH = "cash"
    ASSET = "asset"
    CAPABILITY = "capability"


class RiskAssessment(BaseModel):
    level: RiskLevel = RiskLevel.LOW
    reversible: bool = True
    human_gate_required: bool = False


class PortfolioValueEstimate(BaseModel):
    """Normalized policy estimates kept separate from authoritative financial state."""

    economic_value: float = Field(default=0.0, ge=0.0, le=1.0)
    information_value: float = Field(default=0.0, ge=0.0, le=1.0)
    option_value: float = Field(default=0.0, ge=0.0, le=1.0)
    asset_value: float = Field(default=0.0, ge=0.0, le=1.0)
    feedback_speed: float = Field(default=0.0, ge=0.0, le=1.0)
    uncertainty: float = Field(default=0.0, ge=0.0, le=1.0)
    expected_monetary_value: Decimal | None = None
    expected_value_currency: str | None = Field(default=None, min_length=3, max_length=3)

    @field_validator("expected_monetary_value")
    @classmethod
    def validate_expected_value(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and not value.is_finite():
            raise ValueError("expected monetary value must be finite")
        return value

    @field_validator("expected_value_currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("expected value currency must be a 3-letter code")
        return normalized

    @model_validator(mode="after")
    def validate_monetary_pair(self) -> Self:
        if (self.expected_monetary_value is None) != (self.expected_value_currency is None):
            raise ValueError("expected monetary value and currency must be provided together")
        return self


class PortfolioCandidate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    family_evaluation: FamilyEvaluation
    contract: ExperimentContract
    roles: tuple[PortfolioRole, ...]
    value: PortfolioValueEstimate = Field(default_factory=PortfolioValueEstimate)
    risk: RiskAssessment = Field(default_factory=RiskAssessment)
    capital_requirement: CapitalRequirement | None = None
    group_key: str = Field(min_length=1, max_length=255)

    @field_validator("roles")
    @classmethod
    def validate_roles(cls, roles: tuple[PortfolioRole, ...]) -> tuple[PortfolioRole, ...]:
        if not roles:
            raise ValueError("portfolio candidate requires at least one role")
        if len(set(roles)) != len(roles):
            raise ValueError("portfolio candidate roles cannot contain duplicates")
        return roles

    @field_validator("group_key")
    @classmethod
    def validate_group_key(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("portfolio group_key must be trimmed")
        return value

    @model_validator(mode="after")
    def validate_lineage(self) -> Self:
        evaluation = self.family_evaluation
        if self.contract.id != evaluation.contract_id:
            raise ValueError("portfolio contract does not match family evaluation")
        if self.contract.economic_hypothesis_id != evaluation.hypothesis_id:
            raise ValueError("portfolio contract hypothesis does not match family evaluation")
        if self.contract.business_family != evaluation.family.value:
            raise ValueError("portfolio contract family does not match family evaluation")
        return self

    @property
    def resource_demand(self) -> ResourceVector:
        return self.contract.resource_requirements

    @property
    def current_tier(self) -> EvidenceTier:
        return self.family_evaluation.current_tier

    @property
    def recommendation(self) -> EvaluationRecommendation:
        return self.family_evaluation.recommendation


class PortfolioPlanRequest(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=255)
    candidates: tuple[PortfolioCandidate, ...]
    availability: ResourceAvailability
    base_currency: str = Field(default="USD", min_length=3, max_length=3)
    max_candidates: int = Field(default=10, ge=1)
    exploration_fraction: float = Field(default=0.20, ge=0.0, le=1.0)
    max_group_fraction: float = Field(default=0.50, gt=0.0, le=1.0)
    max_risk: RiskLevel = RiskLevel.MEDIUM
    allow_human_gate: bool = False
    created_at: datetime = Field(default_factory=utcnow)

    @field_validator("idempotency_key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("portfolio idempotency_key must be trimmed")
        return value

    @field_validator("base_currency", mode="before")
    @classmethod
    def normalize_base_currency(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("portfolio base_currency must be a 3-letter alphabetic code")
        return normalized

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("portfolio created_at must be timezone-aware")
        return value

    @model_validator(mode="after")
    def validate_candidates(self) -> Self:
        candidate_ids = [candidate.id for candidate in self.candidates]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("portfolio request cannot contain duplicate candidate IDs")
        return self


class PortfolioCandidateEvaluation(BaseModel):
    candidate_id: UUID
    eligible: bool
    utility: float
    scarcity_pressure: float = Field(ge=0.0)
    selected: bool = False
    rationale: str


class PortfolioAllocation(BaseModel):
    id: UUID
    candidate_id: UUID
    family_evaluation_id: UUID
    hypothesis_id: UUID
    contract_id: UUID
    belief_state_version: int = Field(ge=1)
    current_tier: EvidenceTier
    recommendation: EvaluationRecommendation
    roles: tuple[PortfolioRole, ...]
    group_key: str
    resource_demand: ResourceVector
    value: PortfolioValueEstimate
    risk: RiskAssessment
    capital_requirement: CapitalRequirement | None = None
    utility: float
    scarcity_pressure: float = Field(ge=0.0)
    rationale: str

    @classmethod
    def deterministic_id(cls, plan_key: str, candidate_id: UUID) -> UUID:
        return uuid5(
            NAMESPACE_URL,
            f"business-master/portfolio-allocation/{plan_key}/{candidate_id}",
        )


class PortfolioPlan(BaseModel):
    id: UUID
    idempotency_key: str
    policy_name: str
    policy_version: str
    policy_parameters: dict[str, str | int | float | bool]
    available_resources: ResourceVector
    evaluations: list[PortfolioCandidateEvaluation]
    allocations: list[PortfolioAllocation]
    created_at: datetime

    @classmethod
    def deterministic_id(cls, idempotency_key: str) -> UUID:
        return uuid5(NAMESPACE_URL, f"business-master/portfolio-plan/{idempotency_key}")
