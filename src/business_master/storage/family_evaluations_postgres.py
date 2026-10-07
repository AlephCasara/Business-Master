from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from business_master.domain.family_evaluation import FamilyEvaluation


class FamilyEvaluationConflictError(RuntimeError):
    """Raised when an idempotency key is reused with different evaluation semantics."""


class PostgresFamilyEvaluationStore:
    """Append-only persistence for deterministic business-family evaluations."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def save(self, evaluation: FamilyEvaluation) -> FamilyEvaluation:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            conn.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (evaluation.idempotency_key,),
            )
            existing_row = conn.execute(
                "SELECT * FROM family_evaluation WHERE idempotency_key = %s",
                (evaluation.idempotency_key,),
            ).fetchone()
            if existing_row is not None:
                existing = self._from_row(existing_row)
                if existing != evaluation:
                    raise FamilyEvaluationConflictError(
                        "family evaluation idempotency key was reused with different semantics"
                    )
                return existing

            payload = evaluation.model_dump(mode="json")
            conn.execute(
                """
                INSERT INTO family_evaluation (
                    id, idempotency_key, family, hypothesis_id, contract_id,
                    belief_state_version, current_tier, policy_name, policy_version,
                    evidence_ids, interpretations, criteria, external_observations,
                    independent_sources, replication_count, distinct_contexts,
                    evidence_sufficient, supporting_signal, falsified,
                    economic_readiness, operational_readiness, recommendation,
                    rationale, evaluated_at
                ) VALUES (
                    %(id)s, %(idempotency_key)s, %(family)s, %(hypothesis_id)s,
                    %(contract_id)s, %(belief_state_version)s, %(current_tier)s,
                    %(policy_name)s, %(policy_version)s, %(evidence_ids)s,
                    %(interpretations)s, %(criteria)s, %(external_observations)s,
                    %(independent_sources)s, %(replication_count)s,
                    %(distinct_contexts)s, %(evidence_sufficient)s,
                    %(supporting_signal)s, %(falsified)s, %(economic_readiness)s,
                    %(operational_readiness)s, %(recommendation)s, %(rationale)s,
                    %(evaluated_at)s
                )
                """,
                {
                    "id": evaluation.id,
                    "idempotency_key": evaluation.idempotency_key,
                    "family": evaluation.family.value,
                    "hypothesis_id": evaluation.hypothesis_id,
                    "contract_id": evaluation.contract_id,
                    "belief_state_version": evaluation.belief_state_version,
                    "current_tier": evaluation.current_tier.value,
                    "policy_name": evaluation.policy_name,
                    "policy_version": evaluation.policy_version,
                    "evidence_ids": Jsonb(payload["evidence_ids"]),
                    "interpretations": Jsonb(payload["interpretations"]),
                    "criteria": Jsonb(payload["criteria"]),
                    "external_observations": evaluation.external_observations,
                    "independent_sources": evaluation.independent_sources,
                    "replication_count": evaluation.replication_count,
                    "distinct_contexts": evaluation.distinct_contexts,
                    "evidence_sufficient": evaluation.evidence_sufficient,
                    "supporting_signal": evaluation.supporting_signal,
                    "falsified": evaluation.falsified,
                    "economic_readiness": evaluation.economic_readiness.value,
                    "operational_readiness": evaluation.operational_readiness.value,
                    "recommendation": evaluation.recommendation.value,
                    "rationale": evaluation.rationale,
                    "evaluated_at": evaluation.evaluated_at,
                },
            )
            return evaluation

    def get(self, evaluation_id: UUID) -> FamilyEvaluation | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM family_evaluation WHERE id = %s",
                (evaluation_id,),
            ).fetchone()
        return None if row is None else self._from_row(row)

    def get_by_idempotency_key(self, key: str) -> FamilyEvaluation | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM family_evaluation WHERE idempotency_key = %s",
                (key,),
            ).fetchone()
        return None if row is None else self._from_row(row)

    def list_for_hypothesis(self, hypothesis_id: UUID) -> Sequence[FamilyEvaluation]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            rows = conn.execute(
                """
                SELECT * FROM family_evaluation
                WHERE hypothesis_id = %s
                ORDER BY evaluated_at ASC, id ASC
                """,
                (hypothesis_id,),
            ).fetchall()
        return [self._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row: dict[str, Any]) -> FamilyEvaluation:
        return FamilyEvaluation(
            id=row["id"],
            idempotency_key=row["idempotency_key"],
            family=row["family"],
            hypothesis_id=row["hypothesis_id"],
            contract_id=row["contract_id"],
            belief_state_version=row["belief_state_version"],
            current_tier=row["current_tier"],
            policy_name=row["policy_name"],
            policy_version=row["policy_version"],
            evidence_ids=row["evidence_ids"],
            interpretations=row["interpretations"],
            criteria=row["criteria"],
            external_observations=row["external_observations"],
            independent_sources=row["independent_sources"],
            replication_count=row["replication_count"],
            distinct_contexts=row["distinct_contexts"],
            evidence_sufficient=row["evidence_sufficient"],
            supporting_signal=row["supporting_signal"],
            falsified=row["falsified"],
            economic_readiness=row["economic_readiness"],
            operational_readiness=row["operational_readiness"],
            recommendation=row["recommendation"],
            rationale=row["rationale"],
            evaluated_at=row["evaluated_at"],
        )
