from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module, metadata
from typing import Any, Literal
from uuid import UUID, uuid4

from business_master.optimization.models import (
    ObjectiveDirection,
    OptimizationResult,
    OptimizationRun,
    OptimizationSpec,
    ParameterKind,
    ParameterValue,
    TrialObservation,
    TrialSuggestion,
)
from business_master.optimization.results import result_from_observations


class AxUnavailableError(RuntimeError):
    """Raised when the optional Ax dependency is not installed."""


@dataclass(slots=True)
class _AxRunState:
    run: OptimizationRun
    client: Any
    suggestions: dict[str, TrialSuggestion] = field(default_factory=dict)
    observations: dict[str, TrialObservation] = field(default_factory=dict)


class AxOptimizationEngine:
    """Adapter for Meta Ax's modern ``ax.api.Client`` surface."""

    name = "ax"

    def __init__(self, *, method: Literal["fast", "random_search"] = "fast") -> None:
        client_cls, range_cls, choice_cls = self._load_ax()
        self._client_cls = client_cls
        self._range_cls = range_cls
        self._choice_cls = choice_cls
        self._method = method
        self.version = self._ax_version()
        self._runs: dict[UUID, _AxRunState] = {}

    def create_run(
        self,
        spec: OptimizationSpec,
        *,
        run_id: UUID | None = None,
    ) -> OptimizationRun:
        resolved_id = run_id or uuid4()
        if resolved_id in self._runs:
            raise ValueError(f"optimization run already exists: {resolved_id}")

        client = self._client_cls(random_seed=spec.seed)
        parameter_configs: list[Any] = []
        for parameter in spec.parameters:
            if parameter.kind is ParameterKind.RANGE:
                assert parameter.lower is not None
                assert parameter.upper is not None
                parameter_configs.append(
                    self._range_cls(
                        name=parameter.name,
                        bounds=(float(parameter.lower), float(parameter.upper)),
                        parameter_type=parameter.value_type.value,
                        scaling="log" if parameter.log_scale else None,
                    )
                )
            else:
                parameter_configs.append(
                    self._choice_cls(
                        name=parameter.name,
                        values=list(parameter.values),
                        parameter_type=parameter.value_type.value,
                        is_ordered=parameter.ordered,
                    )
                )

        client.configure_experiment(parameters=parameter_configs, name=spec.name)
        client.configure_optimization(
            objective=self._objective_expression(spec),
            outcome_constraints=[
                f"{constraint.metric} {constraint.operator.value} {constraint.bound}"
                for constraint in spec.outcome_constraints
            ]
            or None,
        )
        client.configure_generation_strategy(
            method=self._method,
            initialization_random_seed=spec.seed,
        )

        run = OptimizationRun(
            id=resolved_id,
            spec=spec,
            engine_name=self.name,
            engine_version=self.version,
        )
        self._runs[resolved_id] = _AxRunState(run=run, client=client)
        return run

    def suggest(self, run_id: UUID, *, count: int = 1) -> list[TrialSuggestion]:
        if count < 1:
            raise ValueError("count must be >= 1")
        state = self._state(run_id)
        generated: dict[int, dict[str, ParameterValue]] = state.client.get_next_trials(
            max_trials=count
        )
        suggestions: list[TrialSuggestion] = []
        for trial_index, parameters in generated.items():
            trial_id = str(trial_index)
            suggestion = TrialSuggestion(
                run_id=run_id,
                trial_id=trial_id,
                parameters=dict(parameters),
                engine_name=self.name,
                engine_trial_id=trial_id,
                generation_method=self._method,
            )
            state.suggestions[trial_id] = suggestion
            suggestions.append(suggestion)
        return suggestions

    def observe(self, observation: TrialObservation) -> None:
        state = self._state(observation.run_id)
        suggestion = state.suggestions.get(observation.trial_id)
        if suggestion is None:
            raise ValueError(f"unknown trial: {observation.trial_id}")
        missing = state.run.spec.required_metrics - observation.metrics.keys()
        if missing:
            raise ValueError(f"observation missing required metrics: {sorted(missing)}")
        assert suggestion.engine_trial_id is not None
        state.client.complete_trial(
            trial_index=int(suggestion.engine_trial_id),
            raw_data=observation.metrics,
        )
        state.observations[observation.trial_id] = observation

    def best(self, run_id: UUID) -> OptimizationResult | None:
        state = self._state(run_id)
        return result_from_observations(
            run_id=run_id,
            spec=state.run.spec,
            suggestions=state.suggestions,
            observations=state.observations,
        )

    def _state(self, run_id: UUID) -> _AxRunState:
        try:
            return self._runs[run_id]
        except KeyError as exc:
            raise KeyError(f"unknown optimization run: {run_id}") from exc

    @staticmethod
    def _objective_expression(spec: OptimizationSpec) -> str:
        return ", ".join(
            (
                f"-{objective.metric}"
                if objective.direction is ObjectiveDirection.MINIMIZE
                else objective.metric
            )
            for objective in spec.objectives
        )

    @staticmethod
    def _load_ax() -> tuple[type[Any], type[Any], type[Any]]:
        try:
            client_module = import_module("ax.api.client")
            configs_module = import_module("ax.api.configs")
        except ModuleNotFoundError as exc:
            raise AxUnavailableError(
                "Ax is optional. Install it with `uv sync --extra ax`."
            ) from exc
        return (
            client_module.Client,
            configs_module.RangeParameterConfig,
            configs_module.ChoiceParameterConfig,
        )

    @staticmethod
    def _ax_version() -> str:
        try:
            return metadata.version("ax-platform")
        except metadata.PackageNotFoundError:
            return "unknown"
