from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Protocol
from uuid import UUID

from business_master.domain.events import DomainEvent
from business_master.domain.models import (
    Decision,
    Experiment,
    Hypothesis,
    MetricSnapshot,
    Resource,
)


class EventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None: ...


class HypothesisRepository(Protocol):
    def get(self, hypothesis_id: UUID) -> Hypothesis | None: ...

    def list_active(self) -> Sequence[Hypothesis]: ...

    def save(self, hypothesis: Hypothesis) -> None: ...


class ExperimentRepository(Protocol):
    def get(self, experiment_id: UUID) -> Experiment | None: ...

    def list_for_hypothesis(self, hypothesis_id: UUID) -> Sequence[Experiment]: ...

    def list_runnable(self) -> Sequence[Experiment]: ...

    def save(self, experiment: Experiment) -> None: ...


class MetricRepository(Protocol):
    def list_for_experiment(self, experiment_id: UUID) -> Sequence[MetricSnapshot]: ...

    def save(self, snapshot: MetricSnapshot) -> None: ...


class DecisionRepository(Protocol):
    def save(self, decision: Decision) -> None: ...


class ResourceRepository(Protocol):
    def list_available(self) -> Sequence[Resource]: ...

    def save(self, resource: Resource) -> None: ...


class WorkDispatcher(Protocol):
    """Runtime-neutral dispatch boundary.

    Hatchet is the initial implementation target, but controllers depend only on this port.
    """

    def dispatch(self, work_type: str, payload: dict[str, object]) -> str: ...

    def dispatch_many(self, work_type: str, payloads: Iterable[dict[str, object]]) -> list[str]: ...


class Clock(Protocol):
    def monotonic(self) -> float: ...
