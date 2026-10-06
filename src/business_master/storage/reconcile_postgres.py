from __future__ import annotations

from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from business_master.controllers.reconciler import ReconcileAction, ReconcileSnapshot
from business_master.domain.models import Decision, Experiment, Hypothesis


class PostgresReconcileStore:
    """Atomic PostgreSQL persistence for reconciliation decisions.

    `commit_create_probe` re-validates the hypothesis inside the same transaction,
    claims a unique action intent, and persists both experiment and decision. A
    process crash rolls the whole transaction back; a successful prior commit makes
    a retry a no-op through the unique idempotency key.
    """

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def build_snapshot(
        self,
        *,
        available_probe_slots: int,
        available_execution_slots: int,
    ) -> ReconcileSnapshot:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            probe_rows = conn.execute(
                """
                SELECT h.id
                FROM hypothesis AS h
                WHERE h.active = true
                  AND h.tier NOT IN ('paused', 'killed')
                  AND NOT EXISTS (
                      SELECT 1
                      FROM experiment AS e
                      WHERE e.hypothesis_id = h.id
                  )
                  AND NOT EXISTS (
                      SELECT 1
                      FROM action_intent AS ai
                      WHERE ai.entity_id = h.id
                        AND ai.action_type = 'create_probe'
                        AND ai.status <> 'cancelled'
                  )
                ORDER BY h.created_at ASC
                LIMIT %s
                """,
                (max(available_probe_slots, 0),),
            ).fetchall()

            runnable_rows = conn.execute(
                """
                SELECT e.id
                FROM experiment AS e
                WHERE e.status IN ('planned', 'queued')
                  AND e.tier NOT IN ('paused', 'killed')
                ORDER BY e.created_at ASC
                LIMIT %s
                """,
                (max(available_execution_slots, 0),),
            ).fetchall()

        return ReconcileSnapshot(
            hypotheses_without_live_experiment=tuple(row["id"] for row in probe_rows),
            runnable_experiments=tuple(row["id"] for row in runnable_rows),
            available_probe_slots=max(available_probe_slots, 0),
            available_execution_slots=max(available_execution_slots, 0),
        )

    def get_hypothesis(self, hypothesis_id: UUID) -> Hypothesis | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM hypothesis WHERE id = %s",
                (hypothesis_id,),
            ).fetchone()
        if row is None:
            return None
        return self._hypothesis_from_row(row)

    def commit_create_probe(
        self,
        *,
        action: ReconcileAction,
        experiment: Experiment,
        decision: Decision,
        idempotency_key: str,
    ) -> bool:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            with conn.transaction():
                hypothesis_row = conn.execute(
                    """
                    SELECT id, active, tier
                    FROM hypothesis
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (action.entity_id,),
                ).fetchone()
                if hypothesis_row is None:
                    return False
                if not hypothesis_row["active"]:
                    return False
                if hypothesis_row["tier"] in {"paused", "killed"}:
                    return False

                existing = conn.execute(
                    "SELECT 1 FROM experiment WHERE hypothesis_id = %s LIMIT 1",
                    (action.entity_id,),
                ).fetchone()
                if existing is not None:
                    return False

                intent_row = conn.execute(
                    """
                    INSERT INTO action_intent (
                        idempotency_key, action_type, entity_id, reason,
                        priority, payload, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                    ON CONFLICT (idempotency_key) DO NOTHING
                    RETURNING id
                    """,
                    (
                        idempotency_key,
                        action.kind.value,
                        action.entity_id,
                        action.reason,
                        action.priority,
                        Jsonb(action.payload),
                    ),
                ).fetchone()
                if intent_row is None:
                    return False

                mutation = (
                    experiment.mutation.model_dump(mode="json")
                    if experiment.mutation is not None
                    else None
                )
                conn.execute(
                    """
                    INSERT INTO experiment (
                        id, hypothesis_id, parent_id, status, tier, business_family,
                        channel_id, product_id, mutation, dimensions,
                        expected_cash_cost, expected_compute_units,
                        expected_human_minutes, created_at, started_at, completed_at
                    ) VALUES (
                        %(id)s, %(hypothesis_id)s, %(parent_id)s, %(status)s,
                        %(tier)s, %(business_family)s, %(channel_id)s,
                        %(product_id)s, %(mutation)s, %(dimensions)s,
                        %(expected_cash_cost)s, %(expected_compute_units)s,
                        %(expected_human_minutes)s, %(created_at)s,
                        %(started_at)s, %(completed_at)s
                    )
                    """,
                    {
                        "id": experiment.id,
                        "hypothesis_id": experiment.hypothesis_id,
                        "parent_id": experiment.parent_id,
                        "status": experiment.status.value,
                        "tier": experiment.tier.value,
                        "business_family": experiment.business_family,
                        "channel_id": experiment.channel_id,
                        "product_id": experiment.product_id,
                        "mutation": Jsonb(mutation) if mutation is not None else None,
                        "dimensions": Jsonb(experiment.dimensions),
                        "expected_cash_cost": experiment.expected_cash_cost,
                        "expected_compute_units": experiment.expected_compute_units,
                        "expected_human_minutes": experiment.expected_human_minutes,
                        "created_at": experiment.created_at,
                        "started_at": experiment.started_at,
                        "completed_at": experiment.completed_at,
                    },
                )

                chosen_action: dict[str, object] = {
                    "action_intent_id": str(intent_row["id"]),
                    "idempotency_key": idempotency_key,
                    "created_experiment_id": str(experiment.id),
                }
                conn.execute(
                    """
                    INSERT INTO decision (
                        id, entity_id, decision_type, policy_name, policy_version,
                        evidence_ids, observed_features, chosen_action,
                        expected_value, expected_cash_cost,
                        expected_compute_units, expected_human_minutes,
                        risk, rationale, created_at
                    ) VALUES (
                        %(id)s, %(entity_id)s, %(decision_type)s,
                        %(policy_name)s, %(policy_version)s, %(evidence_ids)s,
                        %(observed_features)s, %(chosen_action)s,
                        %(expected_value)s, %(expected_cash_cost)s,
                        %(expected_compute_units)s, %(expected_human_minutes)s,
                        %(risk)s, %(rationale)s, %(created_at)s
                    )
                    """,
                    {
                        "id": decision.id,
                        "entity_id": decision.entity_id,
                        "decision_type": decision.decision_type.value,
                        "policy_name": decision.policy_name,
                        "policy_version": decision.policy_version,
                        "evidence_ids": decision.evidence_ids,
                        "observed_features": Jsonb(decision.observed_features),
                        "chosen_action": Jsonb(chosen_action),
                        "expected_value": decision.expected_value,
                        "expected_cash_cost": decision.expected_cash_cost,
                        "expected_compute_units": decision.expected_compute_units,
                        "expected_human_minutes": decision.expected_human_minutes,
                        "risk": decision.risk.value,
                        "rationale": decision.rationale,
                        "created_at": decision.created_at,
                    },
                )

                conn.execute(
                    """
                    UPDATE action_intent
                    SET status = 'completed', updated_at = now()
                    WHERE id = %s
                    """,
                    (intent_row["id"],),
                )

        return True

    @staticmethod
    def _hypothesis_from_row(row: dict[str, Any]) -> Hypothesis:
        return Hypothesis(
            id=row["id"],
            name=row["name"],
            thesis=row["thesis"],
            family=row["family"],
            market=row["market"],
            audience=row["audience"],
            tier=row["tier"],
            parent_id=row["parent_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            active=row["active"],
        )
