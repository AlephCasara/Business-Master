from __future__ import annotations

from uuid import uuid4

import pytest

from business_master.optimization import (
    ConstraintOperator,
    ObjectiveDirection,
    ObjectiveSpec,
    OptimizationSpec,
    OutcomeConstraintSpec,
    ParameterKind,
    ParameterSpec,
    ParameterValueType,
    RandomOptimizationEngine,
    TrialObservation,
)


def _spec(*, multi_objective: bool = False) -> OptimizationSpec:
    objectives = [ObjectiveSpec(metric="margin")]
    if multi_objective:
        objectives.append(ObjectiveSpec(metric="cac", direction=ObjectiveDirection.MINIMIZE))
    return OptimizationSpec(
        name="pricing",
        parameters=(
            ParameterSpec(
                name="price",
                kind=ParameterKind.RANGE,
                value_type=ParameterValueType.FLOAT,
                lower=59,
                upper=99,
            ),
            ParameterSpec(
                name="offer",
                kind=ParameterKind.CHOICE,
                value_type=ParameterValueType.STR,
                values=("plain", "bundle"),
            ),
        ),
        objectives=tuple(objectives),
        outcome_constraints=(
            OutcomeConstraintSpec(
                metric="refund_rate",
                operator=ConstraintOperator.LE,
                bound=0.04,
            ),
        ),
        seed=7,
    )


def test_random_engine_is_reproducible_for_same_seed() -> None:
    left = RandomOptimizationEngine()
    right = RandomOptimizationEngine()
    left_run = left.create_run(_spec())
    right_run = right.create_run(_spec())

    left_parameters = [item.parameters for item in left.suggest(left_run.id, count=4)]
    right_parameters = [item.parameters for item in right.suggest(right_run.id, count=4)]

    assert left_parameters == right_parameters


def test_random_engine_filters_infeasible_observations_before_best() -> None:
    engine = RandomOptimizationEngine()
    run = engine.create_run(_spec())
    first, second = engine.suggest(run.id, count=2)

    engine.observe(
        TrialObservation(
            run_id=run.id,
            trial_id=first.trial_id,
            metrics={"margin": 100.0, "refund_rate": 0.08},
        )
    )
    engine.observe(
        TrialObservation(
            run_id=run.id,
            trial_id=second.trial_id,
            metrics={"margin": 60.0, "refund_rate": 0.02},
        )
    )

    result = engine.best(run.id)

    assert result is not None
    assert result.candidates[0].trial_id == second.trial_id


def test_random_engine_returns_pareto_frontier_for_multiple_objectives() -> None:
    engine = RandomOptimizationEngine()
    run = engine.create_run(_spec(multi_objective=True))
    first, second, third = engine.suggest(run.id, count=3)

    for suggestion, margin, cac in (
        (first, 100.0, 20.0),
        (second, 90.0, 10.0),
        (third, 80.0, 30.0),
    ):
        engine.observe(
            TrialObservation(
                run_id=run.id,
                trial_id=suggestion.trial_id,
                metrics={"margin": margin, "cac": cac, "refund_rate": 0.02},
            )
        )

    result = engine.best(run.id)

    assert result is not None
    assert result.is_pareto_frontier
    assert {candidate.trial_id for candidate in result.candidates} == {
        first.trial_id,
        second.trial_id,
    }


def test_random_engine_requires_all_decision_metrics() -> None:
    engine = RandomOptimizationEngine()
    run = engine.create_run(_spec())
    suggestion = engine.suggest(run.id)[0]

    with pytest.raises(ValueError, match="missing required metrics"):
        engine.observe(
            TrialObservation(
                run_id=run.id,
                trial_id=suggestion.trial_id,
                metrics={"margin": 10.0},
            )
        )


def test_unknown_run_fails_closed() -> None:
    engine = RandomOptimizationEngine()

    with pytest.raises(KeyError, match="unknown optimization run"):
        engine.suggest(uuid4())
