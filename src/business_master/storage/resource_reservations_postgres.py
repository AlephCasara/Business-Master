from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from business_master.domain.clock import utcnow
from business_master.domain.enums import ResourceReservationStatus
from business_master.domain.resources import (
    ResourceAvailability,
    ResourceReservation,
    ResourceReservationRequest,
    ResourceVector,
)


class ResourceReservationError(RuntimeError):
    """Base error for durable resource reservation failures."""


class ResourceNotFoundError(ResourceReservationError):
    def __init__(self, resource_names: Sequence[str]) -> None:
        self.resource_names = tuple(resource_names)
        super().__init__(f"unknown resources: {', '.join(self.resource_names)}")


class ResourceUnavailableError(ResourceReservationError):
    def __init__(self, resource_names: Sequence[str]) -> None:
        self.resource_names = tuple(resource_names)
        super().__init__(f"unavailable resources: {', '.join(self.resource_names)}")


class ResourceCapacityError(ResourceReservationError):
    def __init__(
        self,
        resource_name: str,
        *,
        requested: Decimal,
        available: Decimal,
    ) -> None:
        self.resource_name = resource_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"insufficient capacity for {resource_name}: "
            f"requested={requested} available={available}"
        )


class ReservationConflictError(ResourceReservationError):
    """Raised when an idempotency key is reused for a different reservation request."""


class PostgresResourceReservationStore:
    """Atomic non-fungible resource reservations backed by PostgreSQL.

    Resource rows are locked in deterministic name order before capacity is checked.
    That makes two concurrent requests for the same scarce resource serialize instead
    of both observing stale free capacity and overbooking it.
    """

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def reserve(self, request: ResourceReservationRequest) -> ResourceReservation:
        names = list(request.requirements.quantities)
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            # Serialize retries carrying the same semantic idempotency key even when
            # they request disjoint resource rows.
            conn.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (request.idempotency_key,),
            )

            existing_row = conn.execute(
                "SELECT * FROM resource_reservation WHERE idempotency_key = %s",
                (request.idempotency_key,),
            ).fetchone()
            if existing_row is not None:
                existing = self._reservation_from_row(existing_row)
                self._assert_same_request(existing, request)
                return existing

            resource_rows = conn.execute(
                """
                SELECT id, name, available, capacity
                FROM resource
                WHERE name = ANY(%s)
                ORDER BY name
                FOR UPDATE
                """,
                (names,),
            ).fetchall()

            rows_by_name = {str(row["name"]): row for row in resource_rows}
            missing = sorted(set(names) - set(rows_by_name))
            if missing:
                raise ResourceNotFoundError(missing)

            unavailable = sorted(
                name for name, row in rows_by_name.items() if not bool(row["available"])
            )
            if unavailable:
                raise ResourceUnavailableError(unavailable)

            resource_ids = [row["id"] for row in resource_rows]
            reserved_rows = conn.execute(
                """
                SELECT item.resource_id, COALESCE(SUM(item.amount), 0) AS reserved
                FROM resource_reservation_item AS item
                JOIN resource_reservation AS reservation
                  ON reservation.id = item.reservation_id
                WHERE item.resource_id = ANY(%s)
                  AND reservation.status = 'active'
                GROUP BY item.resource_id
                """,
                (resource_ids,),
            ).fetchall()
            reserved_by_id = {
                row["resource_id"]: Decimal(row["reserved"]) for row in reserved_rows
            }

            for name in names:
                row = rows_by_name[name]
                capacity = Decimal(str(row["capacity"]))
                reserved = reserved_by_id.get(row["id"], Decimal(0))
                free = capacity - reserved
                requested = request.requirements.amount(name)
                if requested > free:
                    raise ResourceCapacityError(
                        name,
                        requested=requested,
                        available=max(free, Decimal(0)),
                    )

            reservation = ResourceReservation(
                id=uuid4(),
                owner_type=request.owner_type,
                owner_id=request.owner_id,
                idempotency_key=request.idempotency_key,
                requirements=request.requirements,
            )
            requirements_payload = reservation.requirements.model_dump(mode="json")[
                "quantities"
            ]
            conn.execute(
                """
                INSERT INTO resource_reservation (
                    id, owner_type, owner_id, idempotency_key, requirements,
                    status, created_at, released_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    reservation.id,
                    reservation.owner_type,
                    reservation.owner_id,
                    reservation.idempotency_key,
                    Jsonb(requirements_payload),
                    reservation.status.value,
                    reservation.created_at,
                    reservation.released_at,
                ),
            )
            for name, amount in reservation.requirements.quantities.items():
                conn.execute(
                    """
                    INSERT INTO resource_reservation_item (reservation_id, resource_id, amount)
                    VALUES (%s, %s, %s)
                    """,
                    (reservation.id, rows_by_name[name]["id"], amount),
                )
            return reservation

    def release(self, reservation_id: UUID) -> ResourceReservation:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM resource_reservation WHERE id = %s FOR UPDATE",
                (reservation_id,),
            ).fetchone()
            if row is None:
                raise ResourceNotFoundError([str(reservation_id)])

            reservation = self._reservation_from_row(row)
            if reservation.status is ResourceReservationStatus.RELEASED:
                return reservation

            released_at = utcnow()
            conn.execute(
                """
                UPDATE resource_reservation
                SET status = 'released', released_at = %s
                WHERE id = %s
                """,
                (released_at, reservation_id),
            )
            return reservation.model_copy(
                update={
                    "status": ResourceReservationStatus.RELEASED,
                    "released_at": released_at,
                }
            )

    def get(self, reservation_id: UUID) -> ResourceReservation | None:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            row = conn.execute(
                "SELECT * FROM resource_reservation WHERE id = %s",
                (reservation_id,),
            ).fetchone()
        if row is None:
            return None
        return self._reservation_from_row(row)

    def availability(self, resource_names: Sequence[str] | None = None) -> ResourceAvailability:
        with psycopg.connect(self._dsn, row_factory=dict_row) as conn:
            if resource_names is None:
                rows = conn.execute(
                    """
                    SELECT resource.name, resource.capacity, resource.available AS enabled,
                           COALESCE(active.reserved, 0) AS reserved
                    FROM resource
                    LEFT JOIN (
                        SELECT item.resource_id, SUM(item.amount) AS reserved
                        FROM resource_reservation_item AS item
                        JOIN resource_reservation AS reservation
                          ON reservation.id = item.reservation_id
                        WHERE reservation.status = 'active'
                        GROUP BY item.resource_id
                    ) AS active ON active.resource_id = resource.id
                    ORDER BY resource.name
                    """
                ).fetchall()
            else:
                names = list(resource_names)
                rows = conn.execute(
                    """
                    SELECT resource.name, resource.capacity, resource.available AS enabled,
                           COALESCE(active.reserved, 0) AS reserved
                    FROM resource
                    LEFT JOIN (
                        SELECT item.resource_id, SUM(item.amount) AS reserved
                        FROM resource_reservation_item AS item
                        JOIN resource_reservation AS reservation
                          ON reservation.id = item.reservation_id
                        WHERE reservation.status = 'active'
                        GROUP BY item.resource_id
                    ) AS active ON active.resource_id = resource.id
                    WHERE resource.name = ANY(%s)
                    ORDER BY resource.name
                    """,
                    (names,),
                ).fetchall()

        capacity: dict[str, Decimal] = {}
        reserved: dict[str, Decimal] = {}
        available: dict[str, Decimal] = {}
        for row in rows:
            name = str(row["name"])
            cap = Decimal(str(row["capacity"]))
            held = Decimal(row["reserved"])
            capacity[name] = cap
            reserved[name] = held
            available[name] = max(cap - held, Decimal(0)) if bool(row["enabled"]) else Decimal(0)

        return ResourceAvailability(
            capacity=ResourceVector(quantities=capacity),
            reserved=ResourceVector(quantities=reserved),
            available=ResourceVector(quantities=available),
        )

    @staticmethod
    def _assert_same_request(
        reservation: ResourceReservation,
        request: ResourceReservationRequest,
    ) -> None:
        if (
            reservation.owner_type != request.owner_type
            or reservation.owner_id != request.owner_id
            or reservation.requirements != request.requirements
        ):
            raise ReservationConflictError(
                "idempotency key already belongs to a different resource reservation"
            )

    @staticmethod
    def _reservation_from_row(row: dict[str, Any]) -> ResourceReservation:
        return ResourceReservation(
            id=row["id"],
            owner_type=row["owner_type"],
            owner_id=row["owner_id"],
            idempotency_key=row["idempotency_key"],
            requirements=ResourceVector(quantities=row["requirements"]),
            status=row["status"],
            created_at=row["created_at"],
            released_at=row["released_at"],
        )
