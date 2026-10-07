from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row

from business_master.domain.belief_updates import (
    BeliefUpdateRecord,
    BeliefUpdateRequest,
    BeliefUpdateResult,
    BoundedLinearBeliefUpdatePolicy,
)
from business_master.domain.beliefs import BeliefState
from business_master.storage.beliefs_postgres import PostgresBeliefStore
from business_master.storage.evidence_postgres import PostgresEvidenceStore


class PostgresBeliefUpdateEngine:
    """Apply evidence to V2 belief state with durable history and idempotency."""

    def __init__(
        self,
        dsn: str,
        policy: BoundedLinearBeliefUpdatePolicy | None = None,
    ) -> None:
        self._dsn = dsn
        self._policy = policy or BoundedLinearBeliefUpdatePolicy()

    def apply(self, request: BeliefUpdateRequest) -> BeliefUpdateResult:
        hypothesis = PostgresBeliefStore(self._dsn).get_economic_hypothesis(
            request.hypothesis_id
        )
        if hypothesis is None:
            raise ValueError("economic hypothesis does not exist")

        evidence = PostgresEvidenceStore(self._dsn).get_record(request.evidence_id)
        if evidence is None:
            raise ValueError("evidence record does not exist")

        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            locked = conn.execute(
                "SELECT id FROM economic_hypothesis WHERE id = %s FOR UPDATE",
                (request.hypothesis_id,),
            ).fetchone()
            if locked is None:
                raise ValueError("economic hypothesis does not exist")

            association = conn.execute(
                """
                SELECT 1
                FROM evidence_association
                WHERE evidence_id = %s
                  AND target_kind = 'economic_hypothesis'
                  AND target_id = %s
                """,
                (request.evidence_id, request.hypothesis_id),
            ).fetchone()
            if association is None:
                raise ValueError("evidence is not associated with the economic hypothesis")

            existing_row = conn.execute(
                """
                SELECT * FROM belief_update
                WHERE hypothesis_id = %s AND evidence_id = %s
                """,
                (request.hypothesis_id, request.evidence_id),
            ).fetchone()
            if existing_row is not None:
                existing = self._update_from_row(existing_row)
                self._assert_retry_matches(existing, request)
                state = self._get_version_conn(
                    conn,
                    request.hypothesis_id,
                    existing.resulting_state_version,
                )
                if state is None:
                    raise RuntimeError("persisted belief update has no resulting state version")
                return BeliefUpdateResult(state=state, update=existing)

            current_row = conn.execute(
                """
                SELECT * FROM belief_state
                WHERE hypothesis_id = %s
                FOR UPDATE
                """,
                (request.hypothesis_id,),
            ).fetchone()
            if current_row is None:
                current = BeliefState(hypothesis_id=request.hypothesis_id)
                self._insert_latest_state(conn, current)
                self._insert_state_version(conn, current)
            else:
                current = BeliefState(**current_row)
                self._insert_state_version(conn, current)

            result = self._policy.apply(
                hypothesis=hypothesis,
                evidence=evidence,
                current=current,
                request=request,
            )

            conn.execute(
                """
                INSERT INTO belief_update (
                    id, hypothesis_id, evidence_id, interpretation, strength,
                    interpretation_rationale, policy_name, policy_version,
                    evidence_class, freshness_weight, effective_weight,
                    prior_state_version, resulting_state_version,
                    confidence_before, confidence_after,
                    uncertainty_before, uncertainty_after,
                    evidence_count_before, evidence_count_after,
                    applied, policy_rationale, evaluated_at, created_at
                ) VALUES (
                    %(id)s, %(hypothesis_id)s, %(evidence_id)s, %(interpretation)s,
                    %(strength)s, %(interpretation_rationale)s, %(policy_name)s,
                    %(policy_version)s, %(evidence_class)s, %(freshness_weight)s,
                    %(effective_weight)s, %(prior_state_version)s,
                    %(resulting_state_version)s, %(confidence_before)s,
                    %(confidence_after)s, %(uncertainty_before)s,
                    %(uncertainty_after)s, %(evidence_count_before)s,
                    %(evidence_count_after)s, %(applied)s, %(policy_rationale)s,
                    %(evaluated_at)s, %(created_at)s
                )
                """,
                self._update_params(result.update),
            )

            if result.update.applied:
                self._insert_state_version(conn, result.state)
                self._update_latest_state(conn, result.state)

            return result

    def get_update(
        self,
        hypothesis_id: UUID,
        evidence_id: UUID,
    ) -> BeliefUpdateRecord | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                """
                SELECT * FROM belief_update
                WHERE hypothesis_id = %s AND evidence_id = %s
                """,
                (hypothesis_id, evidence_id),
            ).fetchone()
        return None if row is None else self._update_from_row(row)

    def list_updates(self, hypothesis_id: UUID) -> Sequence[BeliefUpdateRecord]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            rows = conn.execute(
                """
                SELECT * FROM belief_update
                WHERE hypothesis_id = %s
                ORDER BY created_at ASC, id ASC
                """,
                (hypothesis_id,),
            ).fetchall()
        return [self._update_from_row(row) for row in rows]

    def list_state_history(self, hypothesis_id: UUID) -> Sequence[BeliefState]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            rows = conn.execute(
                """
                SELECT * FROM belief_state_version
                WHERE hypothesis_id = %s
                ORDER BY state_version ASC
                """,
                (hypothesis_id,),
            ).fetchall()
        return [self._state_from_version_row(row) for row in rows]

    @staticmethod
    def _assert_retry_matches(
        existing: BeliefUpdateRecord,
        request: BeliefUpdateRequest,
    ) -> None:
        if (
            existing.interpretation != request.interpretation
            or existing.strength != request.strength
            or existing.interpretation_rationale != request.rationale
        ):
            raise ValueError(
                "evidence has already been evaluated with different update semantics"
            )

    @staticmethod
    def _insert_latest_state(conn: Any, state: BeliefState) -> None:
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
            """,
            state.model_dump(),
        )

    @staticmethod
    def _update_latest_state(conn: Any, state: BeliefState) -> None:
        conn.execute(
            """
            UPDATE belief_state SET
                confidence = %(confidence)s,
                uncertainty = %(uncertainty)s,
                evidence_count = %(evidence_count)s,
                valid_from = %(valid_from)s,
                last_evidence_at = %(last_evidence_at)s,
                freshness = %(freshness)s,
                state_version = %(state_version)s,
                updated_at = %(updated_at)s
            WHERE hypothesis_id = %(hypothesis_id)s
            """,
            state.model_dump(),
        )

    @staticmethod
    def _insert_state_version(conn: Any, state: BeliefState) -> None:
        conn.execute(
            """
            INSERT INTO belief_state_version (
                hypothesis_id, state_version, confidence, uncertainty,
                evidence_count, valid_from, last_evidence_at, freshness, updated_at
            ) VALUES (
                %(hypothesis_id)s, %(state_version)s, %(confidence)s,
                %(uncertainty)s, %(evidence_count)s, %(valid_from)s,
                %(last_evidence_at)s, %(freshness)s, %(updated_at)s
            )
            ON CONFLICT (hypothesis_id, state_version) DO NOTHING
            """,
            state.model_dump(),
        )

    @classmethod
    def _get_version_conn(
        cls,
        conn: Any,
        hypothesis_id: UUID,
        state_version: int,
    ) -> BeliefState | None:
        row = conn.execute(
            """
            SELECT * FROM belief_state_version
            WHERE hypothesis_id = %s AND state_version = %s
            """,
            (hypothesis_id, state_version),
        ).fetchone()
        return None if row is None else cls._state_from_version_row(row)

    @staticmethod
    def _state_from_version_row(row: dict[str, Any]) -> BeliefState:
        return BeliefState(
            hypothesis_id=row["hypothesis_id"],
            confidence=row["confidence"],
            uncertainty=row["uncertainty"],
            evidence_count=row["evidence_count"],
            valid_from=row["valid_from"],
            last_evidence_at=row["last_evidence_at"],
            freshness=row["freshness"],
            state_version=row["state_version"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _update_params(update: BeliefUpdateRecord) -> dict[str, Any]:
        return {
            "id": update.id,
            "hypothesis_id": update.hypothesis_id,
            "evidence_id": update.evidence_id,
            "interpretation": update.interpretation.value,
            "strength": update.strength,
            "interpretation_rationale": update.interpretation_rationale,
            "policy_name": update.policy_name,
            "policy_version": update.policy_version,
            "evidence_class": update.evidence_class.value,
            "freshness_weight": update.freshness_weight,
            "effective_weight": update.effective_weight,
            "prior_state_version": update.prior_state_version,
            "resulting_state_version": update.resulting_state_version,
            "confidence_before": update.confidence_before,
            "confidence_after": update.confidence_after,
            "uncertainty_before": update.uncertainty_before,
            "uncertainty_after": update.uncertainty_after,
            "evidence_count_before": update.evidence_count_before,
            "evidence_count_after": update.evidence_count_after,
            "applied": update.applied,
            "policy_rationale": update.policy_rationale,
            "evaluated_at": update.evaluated_at,
            "created_at": update.created_at,
        }

    @staticmethod
    def _update_from_row(row: dict[str, Any]) -> BeliefUpdateRecord:
        return BeliefUpdateRecord(
            id=row["id"],
            hypothesis_id=row["hypothesis_id"],
            evidence_id=row["evidence_id"],
            interpretation=row["interpretation"],
            strength=row["strength"],
            interpretation_rationale=row["interpretation_rationale"],
            policy_name=row["policy_name"],
            policy_version=row["policy_version"],
            evidence_class=row["evidence_class"],
            freshness_weight=row["freshness_weight"],
            effective_weight=row["effective_weight"],
            prior_state_version=row["prior_state_version"],
            resulting_state_version=row["resulting_state_version"],
            confidence_before=row["confidence_before"],
            confidence_after=row["confidence_after"],
            uncertainty_before=row["uncertainty_before"],
            uncertainty_after=row["uncertainty_after"],
            evidence_count_before=row["evidence_count_before"],
            evidence_count_after=row["evidence_count_after"],
            applied=row["applied"],
            policy_rationale=row["policy_rationale"],
            evaluated_at=row["evaluated_at"],
            created_at=row["created_at"],
        )
