from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from business_master.domain.enums import EvidenceClass, EvidenceTargetKind
from business_master.domain.evidence import EvidenceAssociation, EvidenceRecord


_TARGET_TABLES: dict[EvidenceTargetKind, str] = {
    EvidenceTargetKind.ECONOMIC_HYPOTHESIS: "economic_hypothesis",
    EvidenceTargetKind.EXPERIMENT_CONTRACT: "experiment_contract",
    EvidenceTargetKind.EXPERIMENT: "experiment",
}


class PostgresEvidenceStore:
    """PostgreSQL adapter for immutable V2 evidence and additive associations."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def save_record(self, record: EvidenceRecord) -> None:
        payload = record.model_dump(mode="json")
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            if record.input_evidence_ids:
                rows = conn.execute(
                    "SELECT id FROM evidence_record WHERE id = ANY(%s)",
                    (record.input_evidence_ids,),
                ).fetchall()
                existing_ids = {row["id"] for row in rows}
                missing_ids = set(record.input_evidence_ids) - existing_ids
                if missing_ids:
                    missing = ", ".join(sorted(str(item) for item in missing_ids))
                    raise ValueError(f"input evidence does not exist: {missing}")

            inserted = conn.execute(
                """
                INSERT INTO evidence_record (
                    id, evidence_class, provenance, kind, source, source_event_id,
                    subject_type, subject_id, observed_at, ingested_at, features,
                    payload_ref, schema_version
                ) VALUES (
                    %(id)s, %(evidence_class)s, %(provenance)s, %(kind)s, %(source)s,
                    %(source_event_id)s, %(subject_type)s, %(subject_id)s, %(observed_at)s,
                    %(ingested_at)s, %(features)s, %(payload_ref)s, %(schema_version)s
                )
                ON CONFLICT DO NOTHING
                RETURNING id
                """,
                {
                    "id": record.id,
                    "evidence_class": record.evidence_class.value,
                    "provenance": record.provenance.value,
                    "kind": record.kind,
                    "source": record.source,
                    "source_event_id": record.source_event_id,
                    "subject_type": record.subject_type,
                    "subject_id": record.subject_id,
                    "observed_at": record.observed_at,
                    "ingested_at": record.ingested_at,
                    "features": Jsonb(payload["features"]),
                    "payload_ref": record.payload_ref,
                    "schema_version": record.schema_version,
                },
            ).fetchone()

            if inserted is None:
                row = conn.execute(
                    "SELECT * FROM evidence_record WHERE id = %s",
                    (record.id,),
                ).fetchone()
                if row is None:
                    if record.source_event_id is not None:
                        conflict = conn.execute(
                            """
                            SELECT id FROM evidence_record
                            WHERE source = %s AND source_event_id = %s
                            """,
                            (record.source, record.source_event_id),
                        ).fetchone()
                        if conflict is not None:
                            raise ValueError(
                                "source event is already recorded under a different evidence id"
                            )
                    raise RuntimeError("evidence conflict could not be reloaded")

                input_rows = conn.execute(
                    """
                    SELECT input_evidence_id
                    FROM evidence_input
                    WHERE evidence_id = %s
                    ORDER BY ordinal ASC
                    """,
                    (record.id,),
                ).fetchall()
                persisted = self._record_from_row(
                    row,
                    [input_row["input_evidence_id"] for input_row in input_rows],
                )
                if persisted != record:
                    raise ValueError("evidence record is immutable once persisted")
                return

            for ordinal, input_id in enumerate(record.input_evidence_ids):
                conn.execute(
                    """
                    INSERT INTO evidence_input (evidence_id, input_evidence_id, ordinal)
                    VALUES (%s, %s, %s)
                    """,
                    (record.id, input_id, ordinal),
                )

    def get_record(self, evidence_id: UUID) -> EvidenceRecord | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM evidence_record WHERE id = %s",
                (evidence_id,),
            ).fetchone()
            if row is None:
                return None
            input_rows = conn.execute(
                """
                SELECT input_evidence_id
                FROM evidence_input
                WHERE evidence_id = %s
                ORDER BY ordinal ASC
                """,
                (evidence_id,),
            ).fetchall()

        return self._record_from_row(
            row,
            [input_row["input_evidence_id"] for input_row in input_rows],
        )

    def bind_record(self, association: EvidenceAssociation) -> None:
        target_table = _TARGET_TABLES[association.target_kind]
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            evidence = conn.execute(
                "SELECT id FROM evidence_record WHERE id = %s",
                (association.evidence_id,),
            ).fetchone()
            if evidence is None:
                raise ValueError("cannot bind evidence that has not been persisted")

            target = conn.execute(
                f"SELECT id FROM {target_table} WHERE id = %s",
                (association.target_id,),
            ).fetchone()
            if target is None:
                raise ValueError(f"{association.target_kind.value} target does not exist")

            conn.execute(
                """
                INSERT INTO evidence_association (
                    evidence_id, target_kind, target_id, linked_at
                ) VALUES (%s, %s, %s, %s)
                ON CONFLICT (evidence_id, target_kind, target_id) DO NOTHING
                """,
                (
                    association.evidence_id,
                    association.target_kind.value,
                    association.target_id,
                    association.linked_at,
                ),
            )

    def list_records_for_target(
        self,
        target_kind: EvidenceTargetKind,
        target_id: UUID,
        *,
        evidence_class: EvidenceClass | None = None,
    ) -> Sequence[EvidenceRecord]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            if evidence_class is None:
                rows = conn.execute(
                    """
                    SELECT record.*
                    FROM evidence_record AS record
                    JOIN evidence_association AS association
                      ON association.evidence_id = record.id
                    WHERE association.target_kind = %s
                      AND association.target_id = %s
                    ORDER BY record.observed_at ASC, record.id ASC
                    """,
                    (target_kind.value, target_id),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT record.*
                    FROM evidence_record AS record
                    JOIN evidence_association AS association
                      ON association.evidence_id = record.id
                    WHERE association.target_kind = %s
                      AND association.target_id = %s
                      AND record.evidence_class = %s
                    ORDER BY record.observed_at ASC, record.id ASC
                    """,
                    (target_kind.value, target_id, evidence_class.value),
                ).fetchall()

            records: list[EvidenceRecord] = []
            for row in rows:
                input_rows = conn.execute(
                    """
                    SELECT input_evidence_id
                    FROM evidence_input
                    WHERE evidence_id = %s
                    ORDER BY ordinal ASC
                    """,
                    (row["id"],),
                ).fetchall()
                records.append(
                    self._record_from_row(
                        row,
                        [input_row["input_evidence_id"] for input_row in input_rows],
                    )
                )
        return records

    @staticmethod
    def _record_from_row(
        row: dict[str, Any],
        input_evidence_ids: list[UUID],
    ) -> EvidenceRecord:
        return EvidenceRecord(
            id=row["id"],
            evidence_class=row["evidence_class"],
            provenance=row["provenance"],
            kind=row["kind"],
            source=row["source"],
            source_event_id=row["source_event_id"],
            subject_type=row["subject_type"],
            subject_id=row["subject_id"],
            observed_at=row["observed_at"],
            ingested_at=row["ingested_at"],
            features=row["features"],
            payload_ref=row["payload_ref"],
            input_evidence_ids=input_evidence_ids,
            schema_version=row["schema_version"],
        )
