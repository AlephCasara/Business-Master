from __future__ import annotations

from math import inf, nan
from uuid import uuid4

import pytest
from pydantic import ValidationError

from business_master.optimization.models import (
    ConstraintOperator,
    ObjectiveSpec,
    OptimizationSpec,
    OutcomeConstraintSpec,
    ParameterKind,
    ParameterSpec,
    ParameterValueType,
    TrialObservation,
)


def test_range_parameter_requires_numeric_bounds() -> None:
    with pytest.raises(ValidationError):
        ParameterSpec(
            name="audience",
            kind=ParameterKind.RANGE,
            value_type=ParameterValueType.STR,
            lower=1,
            upper=10,
        )


def test_choice_parameter_requires_matching_values() -> None:
    with pytest.raises(ValidationError):
        ParameterSpec(
            name="offer",
            kind=ParameterKind.CHOICE,
            value_type=ParameterValueType.STR,
            values=("plain", 1),
        )


def test_optimization_spec_requires_unique_parameters() -> None:
    parameter = ParameterSpec(
        name="price",
        kind=ParameterKind.RANGE,
        value_type=ParameterValueType.FLOAT,
        lower=59,
        upper=99,
    )
    with pytest.raises(ValidationError):
        OptimizationSpec(
            name="pricing",
            parameters=(parameter, parameter),
            objectives=(ObjectiveSpec(metric="margin"),),
        )


def test_numeric_parameter_spaces_reject_non_finite_and_non_integral_bounds() -> None:
    with pytest.raises(ValidationError, match="finite"):
        ParameterSpec(
            name="price",
            kind=ParameterKind.RANGE,
            value_type=ParameterValueType.FLOAT,
            lower=0.0,
            upper=inf,
        )

    with pytest.raises(ValidationError, match="integral"):
        ParameterSpec(
            name="quantity",
            kind=ParameterKind.RANGE,
            value_type=ParameterValueType.INT,
            lower=1.5,
            upper=10,
        )


def test_outcome_constraints_reject_non_finite_bounds() -> None:
    with pytest.raises(ValidationError, match="finite"):
        OutcomeConstraintSpec(
            metric="refund_rate",
            operator=ConstraintOperator.LE,
            bound=nan,
        )


def test_trial_observation_rejects_non_finite_metrics_and_duplicate_evidence() -> None:
    run_id = uuid4()
    evidence_id = uuid4()

    with pytest.raises(ValidationError, match="finite"):
        TrialObservation(
            run_id=run_id,
            trial_id="0",
            metrics={"margin": nan},
        )

    with pytest.raises(ValidationError, match="duplicates"):
        TrialObservation(
            run_id=run_id,
            trial_id="0",
            metrics={"margin": 10.0},
            evidence_ids=(evidence_id, evidence_id),
        )
