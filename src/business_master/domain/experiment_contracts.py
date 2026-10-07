from __future__ import annotations

from datetime import datetime
from typing import Any, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from business_master.domain.clock import utcnow
from business_master.domain.enums import (
    ComparisonOperator,
    EvidenceClass,
    MetricAggregation,
)
from business_master.domain.resources import ResourceVector


class MetricCriterion(BaseModel):
    """Machine-readable observation that can support or falsify a contract."""

    metric: str = Field(min_length=1)
    operator: ComparisonOperator
    threshold: float
    evidence_class: EvidenceClass
    aggregation: MetricAggregation = MetricAggregation.LATEST
    minimum_observations: int = Field(default=1, ge=1)


class MeasurementContract(BaseModel):
    """Defines when and how an experiment is allowed to be evaluated."""

    window_seconds: int = Field(gt=0)
    primary_metric: str = Field(min_length=1)
    supporting_criteria: list[MetricCriterion] = Field(default_factory=list)
    falsifying_criteria: list[MetricCriterion] = Field(default_factory=list)
    minimum_external_observations: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_primary_metric(self) -> Self:
        criteria = [*self.supporting_criteria, *self.falsifying_criteria]
        if not criteria:
            raise ValueError("measurement contract requires at least one criterion")
        if self.primary_metric not in {criterion.metric for criterion in criteria}:
            raise ValueError("primary_metric must appear in supporting or falsifying criteria")
        return self


class ExperimentBudget(BaseModel):
    """Legacy scalar V0 envelope retained while callers migrate to ResourceVector."""

    max_cash_cost: float = Field(default=0.0, ge=0.0)
    max_compute_units: float = Field(default=0.0, ge=0.0)
    max_human_minutes: float = Field(default=0.0, ge=0.0)
    max_attempts: int = Field(default=1, ge=1)
    max_external_actions: int = Field(default=1, ge=0)


class ExperimentContract(BaseModel):
    """Immutable pre-execution specification for one bounded economic experiment.

    ``resource_requirements`` is the canonical multidimensional pre-execution demand
    introduced by PR5. ``budget`` remains as a compatibility envelope until legacy
    callers stop expressing cash/compute/human cost as three fungible-ish scalars.
    """

    id: UUID = Field(default_factory=uuid4)
    economic_hypothesis_id: UUID
    business_family: str = Field(min_length=1)
    question: str = Field(min_length=1)
    intervention_dimensions: dict[str, Any] = Field(default_factory=dict)
    held_constant_dimensions: list[str] = Field(default_factory=list)
    expected_observation: str = Field(min_length=1)
    falsification_condition: str = Field(min_length=1)
    measurement: MeasurementContract
    resource_requirements: ResourceVector = Field(default_factory=ResourceVector)
    budget: ExperimentBudget = Field(default_factory=ExperimentBudget)
    parent_contract_id: UUID | None = None
    supersedes_contract_id: UUID | None = None
    origin_decision_id: UUID | None = None
    contract_version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=utcnow)

    @model_validator(mode="after")
    def validate_contract(self) -> Self:
        if self.id in {self.parent_contract_id, self.supersedes_contract_id}:
            raise ValueError("an experiment contract cannot reference itself")
        if len(set(self.held_constant_dimensions)) != len(self.held_constant_dimensions):
            raise ValueError("held_constant_dimensions cannot contain duplicates")
        overlap = set(self.intervention_dimensions).intersection(self.held_constant_dimensions)
        if overlap:
            raise ValueError(
                f"dimensions cannot be both intervened and held constant: {sorted(overlap)}"
            )
        return self


class ExperimentContractBinding(BaseModel):
    """Strangler bridge between a V0 operational Experiment and its V2 contract."""

    experiment_id: UUID
    contract_id: UUID
    bound_at: datetime = Field(default_factory=utcnow)
