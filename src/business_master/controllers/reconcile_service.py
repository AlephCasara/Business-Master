from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from business_master.controllers.experiments import ExperimentController
from business_master.controllers.reconciler import (
    ReconcileAction,
    ReconcileActionType,
    ReconcilePolicy,
    ReconcileSnapshot,
)
from business_master.domain.enums import DecisionType, RiskLevel
from business_master.domain.models import Decision, Experiment, Hypothesis


class ReconcileStore(Protocol):
    def build_snapshot(
        self,
        *,
        available_probe_slots: int,
        available_execution_slots: int,
    ) -> ReconcileSnapshot: ...

    def get_hypothesis(self, hypothesis_id: UUID) -> Hypothesis | None: ...

    def commit_create_probe(
        self,
        *,
        action: ReconcileAction,
        experiment: Experiment,
        decision: Decision,
        idempotency_key: str,
    ) -> bool: ...


@dataclass(frozen=True, slots=True)
class ReconcileRunResult:
    planned_actions: tuple[ReconcileAction, ...]
    created_experiment_ids: tuple[UUID, ...]
    skipped_action_count: int


@dataclass(slots=True)
class ReconcileService:
    """Turn a persisted world-state projection into idempotent durable actions.

    The pure ReconcilePolicy still decides *what* should happen. This service binds
    those decisions to a persistence adapter that can atomically claim an action
    intent and persist its first durable effect.
    """

    store: ReconcileStore
    policy: ReconcilePolicy = ReconcilePolicy()
    experiments: ExperimentController = ExperimentController()

    def run_once(
        self,
        *,
        available_probe_slots: int = 1,
        available_execution_slots: int = 0,
    ) -> ReconcileRunResult:
        snapshot = self.store.build_snapshot(
            available_probe_slots=max(available_probe_slots, 0),
            available_execution_slots=max(available_execution_slots, 0),
        )
        actions = tuple(self.policy.plan(snapshot))
        created: list[UUID] = []
        skipped = 0

        for action in actions:
            if action.kind is not ReconcileActionType.CREATE_PROBE:
                skipped += 1
                continue

            hypothesis = self.store.get_hypothesis(action.entity_id)
            if hypothesis is None:
                skipped += 1
                continue

            experiment = self.experiments.create_probe(hypothesis)
            idempotency_key = f"create_probe:{hypothesis.id}:initial"
            decision = Decision(
                entity_id=hypothesis.id,
                decision_type=DecisionType.CREATE_PROBE,
                policy_name="reconciler",
                policy_version="0.1",
                observed_features={
                    "available_probe_slots": snapshot.available_probe_slots,
                    "business_family": hypothesis.family,
                },
                expected_cash_cost=experiment.expected_cash_cost,
                expected_compute_units=experiment.expected_compute_units,
                expected_human_minutes=experiment.expected_human_minutes,
                risk=RiskLevel.ZERO,
                rationale=action.reason,
            )

            committed = self.store.commit_create_probe(
                action=action,
                experiment=experiment,
                decision=decision,
                idempotency_key=idempotency_key,
            )
            if committed:
                created.append(experiment.id)
            else:
                skipped += 1

        return ReconcileRunResult(
            planned_actions=actions,
            created_experiment_ids=tuple(created),
            skipped_action_count=skipped,
        )
