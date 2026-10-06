from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID


class ReconcileActionType(StrEnum):
    CREATE_PROBE = "create_probe"
    DISPATCH_EXPERIMENT = "dispatch_experiment"
    REQUEST_MEASUREMENT = "request_measurement"
    EVALUATE_EXPERIMENT = "evaluate_experiment"
    REQUEST_HUMAN = "request_human"


@dataclass(frozen=True, slots=True)
class ReconcileAction:
    kind: ReconcileActionType
    entity_id: UUID
    reason: str
    priority: int = 0
    payload: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ReconcileSnapshot:
    """Compact state projection used by the global reconciler.

    The real system computes this projection from PostgreSQL. The reconciler does
    not load the entire world model into memory.
    """

    hypotheses_without_live_experiment: tuple[UUID, ...] = ()
    runnable_experiments: tuple[UUID, ...] = ()
    experiments_due_for_measurement: tuple[UUID, ...] = ()
    experiments_ready_for_evaluation: tuple[UUID, ...] = ()
    open_human_actions: tuple[UUID, ...] = ()
    available_execution_slots: int = 0
    available_probe_slots: int = 0


@dataclass(frozen=True, slots=True)
class ReconcilePolicy:
    max_actions_per_cycle: int = 100

    def plan(self, snapshot: ReconcileSnapshot) -> list[ReconcileAction]:
        actions: list[ReconcileAction] = []

        # Measurements/evaluation preserve feedback loops and therefore outrank
        # producing more work when evidence is waiting to be consumed.
        for experiment_id in snapshot.experiments_due_for_measurement:
            actions.append(
                ReconcileAction(
                    kind=ReconcileActionType.REQUEST_MEASUREMENT,
                    entity_id=experiment_id,
                    reason="External evidence is due for collection.",
                    priority=100,
                )
            )

        for experiment_id in snapshot.experiments_ready_for_evaluation:
            actions.append(
                ReconcileAction(
                    kind=ReconcileActionType.EVALUATE_EXPERIMENT,
                    entity_id=experiment_id,
                    reason="New evidence is available and has not been converted into a decision.",
                    priority=95,
                )
            )

        execution_slots = max(snapshot.available_execution_slots, 0)
        for experiment_id in snapshot.runnable_experiments[:execution_slots]:
            actions.append(
                ReconcileAction(
                    kind=ReconcileActionType.DISPATCH_EXPERIMENT,
                    entity_id=experiment_id,
                    reason="Runnable experiment has available execution capacity.",
                    priority=80,
                )
            )

        probe_slots = max(snapshot.available_probe_slots, 0)
        for hypothesis_id in snapshot.hypotheses_without_live_experiment[:probe_slots]:
            actions.append(
                ReconcileAction(
                    kind=ReconcileActionType.CREATE_PROBE,
                    entity_id=hypothesis_id,
                    reason="Active hypothesis lacks a live bounded experiment and probe capacity exists.",
                    priority=60,
                )
            )

        # Human actions are batched and surfaced but do not starve machine work.
        for action_id in snapshot.open_human_actions:
            actions.append(
                ReconcileAction(
                    kind=ReconcileActionType.REQUEST_HUMAN,
                    entity_id=action_id,
                    reason="A durable workflow is blocked on an explicit human gate.",
                    priority=20,
                )
            )

        actions.sort(key=lambda item: item.priority, reverse=True)
        return actions[: self.max_actions_per_cycle]
