from __future__ import annotations

from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from business_master.domain.beliefs import BeliefState
from business_master.domain.hypotheses import EconomicHypothesis


class PostgresBeliefStore:
    """PostgreSQL adapter for the V2 belief graph.

    It is deliberately separate from the V0 PostgresStore while the strangler
    migration is in progress. Existing hypothesis/runtime persistence remains
    unchanged until consumers are migrated explicitly.
    """

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def save_economic_hypothesis(self, hypothesis: EconomicHypothesis) -> None:
        with psycopg.connect(self._dsn) as conn:
            conn.execute(
                """
                INSERT INTO economic_hypothesis (
                    id, hypothesis_type, subject, proposition, mechanism, context,
                    expected_observation, falsification_condition, evidence_requirements,
                    measurement_window_seconds, freshness_policy, legacy_hypothesis_id,
                    status, created_at, updated_at
                ) VALUES (
                    %(id)s, %(hypothesis_type)s, %(subject)s, %(proposition)s,
                    %(mechanism)s, %(context)s, %(expected_observation)s,
                    %(falsification_condition)s, %(evidence_requirements)s,
                    %(measurement_window_seconds)s, %(freshness_policy)s,
                    %(legacy_hypothesis_id)s, %(status)s, %(created_at)s, %(updated_at)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    hypothesis_type = EXCLUDED.hypothesis_type,
                    subject = EXCLUDED.subject,
                    proposition = EXCLUDED.proposition,
                    mechanism = EXCLUDED.mechanism,
                    context = EXCLUDED.context,
                    expected_observation = EXCLUDED.expected_observation,
                    falsification_condition = EXCLUDED.falsification_condition,
                    evidence_requirements = EXCLUDED.evidence_requirements,
                    measurement_window_seconds = EXCLUDED.measurement_window_seconds,
                    freshness_policy = EXCLUDED.freshness_policy,
                    legacy_hypothesis_id = EXCLUDED.legacy_hypothesis_id,
                    status = EXCLUDED.status,
                    updated_at = EXCLUDED.updated_at
                """,
                {
                    "id": hypothesis.id,
                    "hypothesis_type": hypothesis.hypothesis_type.value,
                    "subject": hypothesis.subject,
                    "proposition": hypothesis.proposition,
                    "mechanism": hypothesis.mechanism,
                    "context": Jsonb(hypothesis.context.model_dump(mode="json")),
                    "expected_observation": hypothesis.expected_observation,
                    "falsification_condition": hypothesis.falsification_condition,
                    "evidence_requirements": Jsonb(
                        hypothesis.evidence_requirements.model_dump(mode="json")
                    ),
                    "measurement_window_seconds": hypothesis.measurement_window_seconds,
                    "freshness_policy": Jsonb(
                        hypothesis.freshness_policy.model_dump(mode="json")
                    ),
                    "legacy_hypothesis_id": hypothesis.legacy_hypothesis_id,
                    "status": hypothesis.status.value,
                    "created_at": hypothesis.created_at,
                    "updated_at": hypothesis.updated_at,
                },
            )

            conn.execute(
                "DELETE FROM economic_hypothesis_parent WHERE hypothesis_id = %s",
                (hypothesis.id,),
            )
            for parent_id in hypothesis.parent_ids:
                conn.execute(
                    """
                    INSERT INTO economic_hypothesis_parent (hypothesis_id, parent_id)
                    VALUES (%s, %s)
                    """,
                    (hypothesis.id, parent_id),
                )

            conn.execute(
                "DELETE FROM economic_hypothesis_dependency WHERE hypothesis_id = %s",
                (hypothesis.id,),
            )
            for dependency_id in hypothesis.dependency_ids:
                conn.execute(
                    """
                    INSERT INTO economic_hypothesis_dependency (hypothesis_id, dependency_id)
                    VALUES (%s, %s)
                    """,
                    (hypothesis.id, dependency_id),
                )

    def get_economic_hypothesis(self, hypothesis_id: UUID) -> EconomicHypothesis | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM economic_hypothesis WHERE id = %s",
                (hypothesis_id,),
            ).fetchone()
            if row is None:
                return None
            parent_rows = conn.execute(
                """
                SELECT parent_id FROM economic_hypothesis_parent
                WHERE hypothesis_id = %s ORDER BY parent_id
                """,
                (hypothesis_id,),
            ).fetchall()
            dependency_rows = conn.execute(
                """
                SELECT dependency_id FROM economic_hypothesis_dependency
                WHERE hypothesis_id = %s ORDER BY dependency_id
                """,
                (hypothesis_id,),
            ).fetchall()

        return self._economic_hypothesis_from_row(
            row,
            parent_ids=[item["parent_id"] for item in parent_rows],
            dependency_ids=[item["dependency_id"] for item in dependency_rows],
        )

    def save_belief_state(self, belief: BeliefState) -> None:
        with psycopg.connect(self._dsn) as conn:
            conn.execute(
                """
                INSERT INTO belief_state (
                    hypothesis_id, confidence, uncertainty, evidence_count,
                    valid_from, last_evidence_at, freshness, state_version, updated_at
                ) VALUES (
                    %(hypothesis_id)s, %(confidence)s, %(uncertainty)s,
                    %(evidence_count)s, %(valid_from)s, %(last_evidence_at)s,
                    %(freshness)s, %(state_version)s, %(updated_at)s
                )
                ON CONFLICT (hypothesis_id) DO UPDATE SET
                    confidence = EXCLUDED.confidence,
                    uncertainty = EXCLUDED.uncertainty,
                    evidence_count = EXCLUDED.evidence_count,
                    valid_from = EXCLUDED.valid_from,
                    last_evidence_at = EXCLUDED.last_evidence_at,
                    freshness = EXCLUDED.freshness,
                    state_version = EXCLUDED.state_version,
                    updated_at = EXCLUDED.updated_at
                """,
                belief.model_dump(),
            )

    def get_belief_state(self, hypothesis_id: UUID) -> BeliefState | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM belief_state WHERE hypothesis_id = %s",
                (hypothesis_id,),
            ).fetchone()
        if row is None:
            return None
        return BeliefState(**row)

    @staticmethod
    def _economic_hypothesis_from_row(
        row: dict[str, Any],
        *,
        parent_ids: list[UUID],
        dependency_ids: list[UUID],
    ) -> EconomicHypothesis:
        return EconomicHypothesis(
            id=row["id"],
            hypothesis_type=row["hypothesis_type"],
            subject=row["subject"],
            proposition=row["proposition"],
            mechanism=row["mechanism"],
            context=row["context"],
            expected_observation=row["expected_observation"],
            falsification_condition=row["falsification_condition"],
            evidence_requirements=row["evidence_requirements"],
            measurement_window_seconds=row["measurement_window_seconds"],
            freshness_policy=row["freshness_policy"],
            parent_ids=parent_ids,
            dependency_ids=dependency_ids,
            legacy_hypothesis_id=row["legacy_hypothesis_id"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
