from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from business_master.optimization.models import (
    ConstraintOperator,
    ObjectiveDirection,
    OptimizationCandidate,
    OptimizationResult,
    OptimizationSpec,
    TrialObservation,
    TrialSuggestion,
)


def result_from_observations(
    *,
    run_id: UUID,
    spec: OptimizationSpec,
    suggestions: Mapping[str, TrialSuggestion],
    observations: Mapping[str, TrialObservation],
) -> OptimizationResult | None:
    feasible = [
        _candidate(suggestions, observation)
        for observation in observations.values()
        if _is_feasible(spec, observation)
    ]
    if not feasible:
        return None

    if len(spec.objectives) == 1:
        objective = spec.objectives[0]
        reverse = objective.direction is ObjectiveDirection.MAXIMIZE
        best = sorted(
            feasible,
            key=lambda candidate: candidate.metrics[objective.metric],
            reverse=reverse,
        )[0]
        return OptimizationResult(run_id=run_id, candidates=(best,))

    frontier = tuple(
        candidate
        for candidate in feasible
        if not any(
            other.trial_id != candidate.trial_id
            and _dominates(spec, other, candidate)
            for other in feasible
        )
    )
    return OptimizationResult(
        run_id=run_id,
        candidates=frontier,
        is_pareto_frontier=True,
    )


def _candidate(
    suggestions: Mapping[str, TrialSuggestion],
    observation: TrialObservation,
) -> OptimizationCandidate:
    suggestion = suggestions[observation.trial_id]
    return OptimizationCandidate(
        trial_id=observation.trial_id,
        parameters=suggestion.parameters,
        metrics=observation.metrics,
    )


def _is_feasible(spec: OptimizationSpec, observation: TrialObservation) -> bool:
    for constraint in spec.outcome_constraints:
        value = observation.metrics[constraint.metric]
        if constraint.operator is ConstraintOperator.GE and value < constraint.bound:
            return False
        if constraint.operator is ConstraintOperator.LE and value > constraint.bound:
            return False
    return True


def _dominates(
    spec: OptimizationSpec,
    left: OptimizationCandidate,
    right: OptimizationCandidate,
) -> bool:
    at_least_as_good = True
    strictly_better = False
    for objective in spec.objectives:
        left_value = left.metrics[objective.metric]
        right_value = right.metrics[objective.metric]
        if objective.direction is ObjectiveDirection.MAXIMIZE:
            at_least_as_good = at_least_as_good and left_value >= right_value
            strictly_better = strictly_better or left_value > right_value
        else:
            at_least_as_good = at_least_as_good and left_value <= right_value
            strictly_better = strictly_better or left_value < right_value
    return at_least_as_good and strictly_better
