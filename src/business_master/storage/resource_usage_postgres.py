from __future__ import annotations

from typing import Any
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from business_master.domain.clock import utcnow
from business_master.domain.resources import ResourceUsage, ResourceUsageRequest, ResourceVector
from business_master.storage.resource_reservations_postgres import (
    ReservationNotFoundError,
    ResourceNotFoundError,
)


class ResourceUsageError(RuntimeError):
    """Base error for durable resource-usage recording failures."""


class ResourceUsageConflictError(ResourceUsageError):
    """Raised when an idempotency key is reused for different observed usage."""


class PostgresResourceUsageStore:
    """Persist actual observed resource usage independently from reservations."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def record(self, request: ResourceUsageRequest) -> ResourceUsage:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            conn.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (request.idempotency_key,),
            )

            existing_row = conn.execute(
                "SELECT * FROM resource_usage WHERE idempotency_key = %s",
                (request.idempotency_key,),
            ).fetchone()
            if existing_row is not None:
                existing = self._usage_from_row(existing_row)
                self._assert_same_request(existing, request)
                return existing

            reservation_row = conn.execute(
                "SELECT id FROM resource_reservation WHERE id = %s",
                (request.reservation_id,),
            ).fetchone()
            if reservation_row is None:
                raise ReservationNotFoundError(request.reservation_id)

            resource_names = list(request.actual.quantities)
            known_rows = conn.execute(
                "SELECT name FROM resource WHERE name = ANY(%s)",
                (resource_names,),
            ).fetchall()
            known_names = {str(row["name"]) for row in known_rows}
            missing = sorted(set(resource_names) - known_names)
            if missing:
                raise ResourceNotFoundError(missing)

            usage = ResourceUsage(
                id=uuid4(),
                reservation_id=request.reservation_id,
                execution_id=request.execution_id,
                idempotency_key=request.idempotency_key,
                actual=request.actual,
                observed_at=utcnow(),
            )
            actual_payload = usage.actual.model_dump(mode="json")["quantities"]
            conn.execute(
                """
                INSERT INTO resource_usage (
                    id, reservation_id, execution_id, idempotency_key, actual, observed_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    usage.id,
                    usage.reservation_id,
                    usage.execution_id,
                    usage.idempotency_key,
                    Jsonb(actual_payload),
                    usage.observed_at,
                ),
            )
            return usage

    def get(self, usage_id: object) -> ResourceUsage | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM resource_usage WHERE id = %s",
                (usage_id,),
            ).fetchone()
        if row is None:
            return None
        return self._usage_from_row(row)

    def list_for_reservation(self, reservation_id: object) -> list[ResourceUsage]:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM resource_usage
                WHERE reservation_id = %s
                ORDER BY observed_at, id
                """,
                (reservation_id,),
            ).fetchall()
        return [self._usage_from_row(row) for row in rows]

    @staticmethod
    def _assert_same_request(usage: ResourceUsage, request: ResourceUsageRequest) -> None:
        if (
            usage.reservation_id != request.reservation_id
            or usage.execution_id != request.execution_id
            or usage.actual != request.actual
        ):
            raise ResourceUsageConflictError(
                "idempotency key already belongs to different resource usage"
            )

    @staticmethod
    def _usage_from_row(row: dict[str, Any]) -> ResourceUsage:
        return ResourceUsage(
            id=row["id"],
            reservation_id=row["reservation_id"],
            execution_id=row["execution_id"],
            idempotency_key=row["idempotency_key"],
            actual=ResourceVector(quantities=row["actual"]),
            observed_at=row["observed_at"],
        )
