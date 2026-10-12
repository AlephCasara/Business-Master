from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from math import isfinite
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from business_master.domain.clock import utcnow

type ParameterValue = float | int | str | bool

_NAME_PATTERN = r"^[A-Za-z_][A-Za-z0-9_]*$"


class ParameterKind(StrEnum):
    RANGE = "range"
    CHOICE = "choice"


class ParameterValueType(StrEnum):
    FLOAT = "float"
    INT = "int"
    STR = "str"
    BOOL = "bool"


class ObjectiveDirection(StrEnum):
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


class ConstraintOperator(StrEnum):
    GE = ">="
    LE = "<="


class ParameterSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, pattern=_NAME_PATTERN)
    kind: ParameterKind
    value_type: ParameterValueType
    lower: float | int | None = None
    upper: float | int | None = None
    values: tuple[ParameterValue, ...] = ()
    log_scale: bool = False
    ordered: bool | None = None

    @model_validator(mode="after")
    def validate_shape(self) -> ParameterSpec:
        if self.kind is ParameterKind.RANGE:
            if self.value_type not in {ParameterValueType.FLOAT, ParameterValueType.INT}:
                raise ValueError("range parameters must be float or int")
            if self.lower is None or self.upper is None:
                raise ValueError("range parameters require lower and upper bounds")
            if not isfinite(float(self.lower)) or not isfinite(float(self.upper)):
                raise ValueError("range bounds must be finite")
            if self.value_type is ParameterValueType.INT and (
                not float(self.lower).is_integer() or not float(self.upper).is_integer()
            ):
                raise ValueError("integer range bounds must be integral")
            if self.lower >= self.upper:
                raise ValueError("range lower bound must be smaller than upper bound")
            if self.values:
                raise ValueError("range parameters cannot define choice values")
            if self.log_scale and self.lower <= 0:
                raise ValueError("log-scaled ranges require a positive lower bound")
        else:
            if len(self.values) < 2:
                raise ValueError("choice parameters require at least two values")
            if len(set(self.values)) != len(self.values):
                raise ValueError("choice parameter values must be unique")
            if self.lower is not None or self.upper is not None:
                raise ValueError("choice parameters cannot define range bounds")
            if self.log_scale:
                raise ValueError("choice parameters do not use log_scale")
            if not all(self._matches_value_type(value) for value in self.values):
                raise ValueError("choice values do not match value_type")
            if self.value_type is ParameterValueType.FLOAT and not all(
                isfinite(float(value)) for value in self.values
            ):
                raise ValueError("numeric choice values must be finite")
        return self

    def _matches_value_type(self, value: ParameterValue) -> bool:
        if self.value_type is ParameterValueType.BOOL:
            return isinstance(value, bool)
        if self.value_type is ParameterValueType.INT:
            return isinstance(value, int) and not isinstance(value, bool)
        if self.value_type is ParameterValueType.FLOAT:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        return isinstance(value, str)


class ObjectiveSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    metric: str = Field(min_length=1, pattern=_NAME_PATTERN)
    direction: ObjectiveDirection = ObjectiveDirection.MAXIMIZE


class OutcomeConstraintSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    metric: str = Field(min_length=1, pattern=_NAME_PATTERN)
    operator: ConstraintOperator
    bound: float

    @model_validator(mode="after")
    def validate_bound(self) -> OutcomeConstraintSpec:
        if not isfinite(self.bound):
            raise ValueError("outcome constraint bound must be finite")
        return self


class OptimizationSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    hypothesis_id: UUID | None = None
    experiment_contract_id: UUID | None = None
    parameters: tuple[ParameterSpec, ...]
    objectives: tuple[ObjectiveSpec, ...]
    outcome_constraints: tuple[OutcomeConstraintSpec, ...] = ()
    seed: int = 0

    @model_validator(mode="after")
    def validate_spec(self) -> OptimizationSpec:
        if not self.parameters:
            raise ValueError("optimization requires at least one parameter")
        if not self.objectives:
            raise ValueError("optimization requires at least one objective")
        parameter_names = [parameter.name for parameter in self.parameters]
        if len(set(parameter_names)) != len(parameter_names):
            raise ValueError("parameter names must be unique")
        objective_metrics = [objective.metric for objective in self.objectives]
        if len(set(objective_metrics)) != len(objective_metrics):
            raise ValueError("objective metrics must be unique")
        return self

    @property
    def required_metrics(self) -> frozenset[str]:
        return frozenset(
            [objective.metric for objective in self.objectives]
            + [constraint.metric for constraint in self.outcome_constraints]
        )


class OptimizationRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    spec: OptimizationSpec
    engine_name: str
    engine_version: str
    created_at: datetime = Field(default_factory=utcnow)


class TrialSuggestion(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: UUID
    trial_id: str
    parameters: dict[str, ParameterValue]
    engine_name: str
    engine_trial_id: str | None = None
    generation_method: str | None = None
    created_at: datetime = Field(default_factory=utcnow)

    @model_validator(mode="after")
    def validate_parameters(self) -> TrialSuggestion:
        for value in self.parameters.values():
            if isinstance(value, float) and not isfinite(value):
                raise ValueError("trial parameters must be finite")
        return self


class TrialObservation(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: UUID
    trial_id: str
    metrics: dict[str, float]
    evidence_ids: tuple[UUID, ...] = ()
    observed_at: datetime = Field(default_factory=utcnow)

    @model_validator(mode="after")
    def validate_observation(self) -> TrialObservation:
        if not self.metrics:
            raise ValueError("trial observation requires at least one metric")
        if not all(isfinite(value) for value in self.metrics.values()):
            raise ValueError("trial metrics must be finite")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("evidence_ids cannot contain duplicates")
        return self


class OptimizationCandidate(BaseModel):
    model_config = ConfigDict(frozen=True)

    trial_id: str
    parameters: dict[str, ParameterValue]
    metrics: dict[str, float]


class OptimizationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: UUID
    candidates: tuple[OptimizationCandidate, ...]
    is_pareto_frontier: bool = False
