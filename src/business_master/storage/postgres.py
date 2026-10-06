from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from business_master.domain.events import DomainEvent
from business_master.domain.models import (
    Decision,
    Experiment,
    Hypothesis,
    MetricSnapshot,
    Resource,
)


class PostgresStore:
    """Small explicit PostgreSQL adapter for the bootstrap world model.

    Domain policy does not depend on this class. It intentionally keeps SQL visible
    and versioned while the schema is still evolving rapidly.
    """

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def save_hypothesis(self, hypothesis: Hypothesis) -> None:
        with psycopg.connect(self._dsn) as conn:
            conn.execute(
                """
                INSERT INTO hypothesis (
                    id, name, thesis, family, market, audience, tier, parent_id,
                    active, created_at, updated_at
                ) VALUES (
                    %(id)s, %(name)s, %(thesis)s, %(family)s, %(market)s, %(audience)s,
                    %(tier)s, %(parent_id)s, %(active)s, %(created_at)s, %(updated_at)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    thesis = EXCLUDED.thesis,
                    family = EXCLUDED.family,
                    market = EXCLUDED.market,
                    audience = EXCLUDED.audience,
                    tier = EXCLUDED.tier,
                    parent_id = EXCLUDED.parent_id,
                    active = EXCLUDED.active,
                    updated_at = EXCLUDED.updated_at
                """,
                {
                    "id": hypothesis.id,
                    "name": hypothesis.name,
                    "thesis": hypothesis.thesis,
                    "family": hypothesis.family,
                    "market": hypothesis.market,
                    "audience": hypothesis.audience,
                    "tier": hypothesis.tier.value,
                    "parent_id": hypothesis.parent_id,
                    "active": hypothesis.active,
                    "created_at": hypothesis.created_at,
                    "updated_at": hypothesis.updated_at,
                },
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

    def list_active_hypotheses(self) -> Sequence[Hypothesis]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            rows = conn.execute(
                "SELECT * FROM hypothesis WHERE active = true ORDER BY created_at ASC"
            ).fetchall()
        return [self._hypothesis_from_row(row) for row in rows]

    def save_experiment(self, experiment: Experiment) -> None:
        mutation = experiment.mutation.model_dump(mode="json") if experiment.mutation else None
        with psycopg.connect(self._dsn) as conn:
            conn.execute(
                """
                INSERT INTO experiment (
                    id, hypothesis_id, parent_id, status, tier, business_family,
                    channel_id, product_id, mutation, dimensions,
                    expected_cash_cost, expected_compute_units, expected_human_minutes,
                    created_at, started_at, completed_at
                ) VALUES (
                    %(id)s, %(hypothesis_id)s, %(parent_id)s, %(status)s, %(tier)s,
                    %(business_family)s, %(channel_id)s, %(product_id)s, %(mutation)s,
                    %(dimensions)s, %(expected_cash_cost)s, %(expected_compute_units)s,
                    %(expected_human_minutes)s, %(created_at)s, %(started_at)s, %(completed_at)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    status = EXCLUDED.status,
                    tier = EXCLUDED.tier,
                    channel_id = EXCLUDED.channel_id,
                    product_id = EXCLUDED.product_id,
                    mutation = EXCLUDED.mutation,
                    dimensions = EXCLUDED.dimensions,
                    expected_cash_cost = EXCLUDED.expected_cash_cost,
                    expected_compute_units = EXCLUDED.expected_compute_units,
                    expected_human_minutes = EXCLUDED.expected_human_minutes,
                    started_at = EXCLUDED.started_at,
                    completed_at = EXCLUDED.completed_at
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

    def get_experiment(self, experiment_id: UUID) -> Experiment | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM experiment WHERE id = %s",
                (experiment_id,),
            ).fetchone()
        if row is None:
            return None
        return self._experiment_from_row(row)

    def list_runnable_experiments(self) -> Sequence[Experiment]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            rows = conn.execute(
                """
                SELECT * FROM experiment
                WHERE status IN ('planned', 'queued')
                  AND tier NOT IN ('paused', 'killed')
                ORDER BY created_at ASC
                """
            ).fetchall()
        return [self._experiment_from_row(row) for row in rows]

    def save_metric(self, snapshot: MetricSnapshot) -> None:
        with psycopg.connect(self._dsn) as conn:
            conn.execute(
                """
                INSERT INTO metric_snapshot (
                    id, experiment_id, observed_at, age_seconds, metrics, source, external
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    snapshot.id,
                    snapshot.experiment_id,
                    snapshot.observed_at,
                    snapshot.age_seconds,
                    Jsonb(snapshot.metrics),
                    snapshot.source,
                    snapshot.external,
                ),
            )

    def list_metrics(self, experiment_id: UUID) -> Sequence[MetricSnapshot]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            rows = conn.execute(
                """
                SELECT * FROM metric_snapshot
                WHERE experiment_id = %s
                ORDER BY observed_at ASC
                """,
                (experiment_id,),
            ).fetchall()
        return [
            MetricSnapshot(
                id=row["id"],
                experiment_id=row["experiment_id"],
                observed_at=row["observed_at"],
                age_seconds=row["age_seconds"],
                metrics=row["metrics"],
                source=row["source"],
                external=row["external"],
            )
            for row in rows
        ]

    def save_decision(
        self,
        decision: Decision,
        chosen_action: dict[str, object] | None = None,
    ) -> None:
        with psycopg.connect(self._dsn) as conn:
            conn.execute(
                """
                INSERT INTO decision (
                    id, entity_id, decision_type, policy_name, policy_version,
                    evidence_ids, observed_features, chosen_action, expected_value,
                    expected_cash_cost, expected_compute_units, expected_human_minutes,
                    risk, rationale, created_at
                ) VALUES (
                    %(id)s, %(entity_id)s, %(decision_type)s, %(policy_name)s,
                    %(policy_version)s, %(evidence_ids)s, %(observed_features)s,
                    %(chosen_action)s, %(expected_value)s, %(expected_cash_cost)s,
                    %(expected_compute_units)s, %(expected_human_minutes)s,
                    %(risk)s, %(rationale)s, %(created_at)s
                )
                ON CONFLICT (id) DO NOTHING
                """,
                {
                    "id": decision.id,
                    "entity_id": decision.entity_id,
                    "decision_type": decision.decision_type.value,
                    "policy_name": decision.policy_name,
                    "policy_version": decision.policy_version,
                    "evidence_ids": decision.evidence_ids,
                    "observed_features": Jsonb(decision.observed_features),
                    "chosen_action": Jsonb(chosen_action or {}),
                    "expected_value": decision.expected_value,
                    "expected_cash_cost": decision.expected_cash_cost,
                    "expected_compute_units": decision.expected_compute_units,
                    "expected_human_minutes": decision.expected_human_minutes,
                    "risk": decision.risk.value,
                    "rationale": decision.rationale,
                    "created_at": decision.created_at,
                },
            )

    def save_resource(self, resource: Resource) -> None:
        with psycopg.connect(self._dsn) as conn:
            conn.execute(
                """
                INSERT INTO resource (id, name, kind, available, capacity, labels, last_seen_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    kind = EXCLUDED.kind,
                    available = EXCLUDED.available,
                    capacity = EXCLUDED.capacity,
                    labels = EXCLUDED.labels,
                    last_seen_at = EXCLUDED.last_seen_at
                """,
                (
                    resource.id,
                    resource.name,
                    resource.kind.value,
                    resource.available,
                    resource.capacity,
                    Jsonb(resource.labels),
                    resource.last_seen_at,
                ),
            )

    def append_event(self, event: DomainEvent) -> None:
        with psycopg.connect(self._dsn) as conn:
            conn.execute(
                """
                INSERT INTO domain_event (
                    id, name, aggregate_type, aggregate_id, occurred_at,
                    causation_id, correlation_id, payload, schema_version
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    event.id,
                    event.name,
                    event.aggregate_type,
                    event.aggregate_id,
                    event.occurred_at,
                    event.causation_id,
                    event.correlation_id,
                    Jsonb(event.payload),
                    event.schema_version,
                ),
            )

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

    @staticmethod
    def _experiment_from_row(row: dict[str, Any]) -> Experiment:
        return Experiment(
            id=row["id"],
            hypothesis_id=row["hypothesis_id"],
            parent_id=row["parent_id"],
            status=row["status"],
            tier=row["tier"],
            business_family=row["business_family"],
            channel_id=row["channel_id"],
            product_id=row["product_id"],
            mutation=row["mutation"],
            dimensions=row["dimensions"],
            expected_cash_cost=float(row["expected_cash_cost"]),
            expected_compute_units=row["expected_compute_units"],
            expected_human_minutes=row["expected_human_minutes"],
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
        )
