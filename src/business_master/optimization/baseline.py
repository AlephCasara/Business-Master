from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from business_master.optimization.models import (
    OptimizationResult,
    OptimizationRun,
    OptimizationSpec,
    ParameterKind,
    ParameterSpec,
    ParameterValue,
    ParameterValueType,
    TrialObservation,
    TrialSuggestion,
)
from business_master.optimization.results import result_from_observations


@dataclass(slots=True)
class _RunState:
    run: OptimizationRun
    rng: random.Random
    next_trial: int = 0
    suggestions: dict[str, TrialSuggestion] = field(default_factory=dict)
    observations: dict[str, TrialObservation] = field(default_factory=dict)


class RandomOptimizationEngine:
    """In-memory random-search baseline for standalone use and comparisons."""

    name = "random"
    version = "1"

    def __init__(self) -> None:
        self._runs: dict[UUID, _RunState] = {}

    def create_run(
        self,
        spec: OptimizationSpec,
        *,
        run_id: UUID | None = None,
    ) -> OptimizationRun:
        resolved_id = run_id or uuid4()
        if resolved_id in self._runs:
            raise ValueError(f"optimization run already exists: {resolved_id}")
        run = OptimizationRun(
            id=resolved_id,
            spec=spec,
            engine_name=self.name,
            engine_version=self.version,
        )
        self._runs[resolved_id] = _RunState(run=run, rng=random.Random(spec.seed))
        return run

    def suggest(self, run_id: UUID, *, count: int = 1) -> list[TrialSuggestion]:
        if count < 1:
            raise ValueError("count must be >= 1")
        state = self._state(run_id)
        suggestions: list[TrialSuggestion] = []
        for _ in range(count):
            trial_id = str(state.next_trial)
            state.next_trial += 1
            suggestion = TrialSuggestion(
                run_id=run_id,
                trial_id=trial_id,
                parameters={
                    parameter.name: self._sample(parameter, state.rng)
                    for parameter in state.run.spec.parameters
                },
                engine_name=self.name,
                engine_trial_id=trial_id,
                generation_method="random",
            )
            state.suggestions[trial_id] = suggestion
            suggestions.append(suggestion)
        return suggestions

    def observe(self, observation: TrialObservation) -> None:
        state = self._state(observation.run_id)
        if observation.trial_id not in state.suggestions:
            raise ValueError(f"unknown trial: {observation.trial_id}")
        missing = state.run.spec.required_metrics - observation.metrics.keys()
        if missing:
            raise ValueError(f"observation missing required metrics: {sorted(missing)}")
        state.observations[observation.trial_id] = observation

    def best(self, run_id: UUID) -> OptimizationResult | None:
        state = self._state(run_id)
        return result_from_observations(
            run_id=run_id,
            spec=state.run.spec,
            suggestions=state.suggestions,
            observations=state.observations,
        )

    def _state(self, run_id: UUID) -> _RunState:
        try:
            return self._runs[run_id]
        except KeyError as exc:
            raise KeyError(f"unknown optimization run: {run_id}") from exc

    @staticmethod
    def _sample(parameter: ParameterSpec, rng: random.Random) -> ParameterValue:
        if parameter.kind is ParameterKind.CHOICE:
            return rng.choice(parameter.values)
        assert parameter.lower is not None
        assert parameter.upper is not None
        if parameter.log_scale:
            value = math.exp(
                rng.uniform(math.log(float(parameter.lower)), math.log(float(parameter.upper)))
            )
        else:
            value = rng.uniform(float(parameter.lower), float(parameter.upper))
        if parameter.value_type is ParameterValueType.INT:
            return max(int(parameter.lower), min(int(parameter.upper), round(value)))
        return value
