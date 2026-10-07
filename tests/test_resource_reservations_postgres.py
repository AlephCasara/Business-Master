from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from threading import Barrier
from uuid import uuid4

import psycopg
import pytest

from business_master.domain.clock import utcnow
from business_master.domain.enums import ResourceKind, ResourceReservationStatus
from business_master.domain.resources import Resource, ResourceReservationRequest, ResourceVector
from business_master.storage.postgres import PostgresStore
from business_master.storage.resource_reservations_postgres import (
    PostgresResourceReservationStore,
    ReservationConflictError,
    ReservationNotDueError,
    ResourceCapacityError,
    ResourceNotFoundError,
    ResourceUnavailableError,
)


@pytest.fixture()
def postgres_dsn() -> str:
    dsn = os.environ.get("BM_TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("BM_TEST_DATABASE_URL is not configured")

    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("DROP SCHEMA IF EXISTS public CASCADE")
        conn.execute("CREATE SCHEMA public")
        migrations = sorted(Path("db/migrations").glob("*.sql"))
        for migration in migrations:
            statements = [
                statement.strip()
                for statement in migration.read_text().split(";")
                if statement.strip()
            ]
            for statement in statements:
                conn.execute(statement)

    return dsn


def _seed_resources(dsn: str) -> None:
    store = PostgresStore(dsn)
    store.save_resource(
        Resource(
            name="cash.usd",
            kind=ResourceKind.CASH,
            capacity=Decimal("100"),
            labels={"unit": "USD"},
        )
    )
    store.save_resource(
        Resource(
            name="gpu.local",
            kind=ResourceKind.GPU,
            capacity=Decimal("1"),
            labels={"unit": "slot"},
        )
    )


def test_reservation_is_idempotent_and_release_restores_capacity(postgres_dsn: str) -> None:
    _seed_resources(postgres_dsn)
    store = PostgresResourceReservationStore(postgres_dsn)
    owner_id = uuid4()
    request = ResourceReservationRequest(
        owner_type="experiment_contract",
        owner_id=owner_id,
        idempotency_key="contract:alpha:reserve",
        requirements=ResourceVector(
            quantities={"cash.usd": Decimal("70"), "gpu.local": Decimal("1")}
        ),
    )

    first = store.reserve(request)
    duplicate = store.reserve(request)

    assert duplicate.id == first.id
    assert store.availability().available.amount("cash.usd") == Decimal("30")
    assert store.availability().available.amount("gpu.local") == Decimal("0")

    with pytest.raises(ResourceCapacityError, match="cash.usd"):
        store.reserve(
            ResourceReservationRequest(
                owner_type="experiment_contract",
                owner_id=uuid4(),
                idempotency_key="contract:beta:reserve",
                requirements=ResourceVector(quantities={"cash.usd": Decimal("40")}),
            )
        )

    with pytest.raises(ReservationConflictError, match="idempotency key"):
        store.reserve(
            ResourceReservationRequest(
                owner_type="experiment_contract",
                owner_id=owner_id,
                idempotency_key=request.idempotency_key,
                requirements=ResourceVector(quantities={"cash.usd": Decimal("60")}),
            )
        )

    released = store.release(first.id)
    released_again = store.release(first.id)

    assert released.status is ResourceReservationStatus.RELEASED
    assert released_again.id == released.id
    assert released_again.released_at == released.released_at
    assert store.availability().available.amount("cash.usd") == Decimal("100")
    assert store.availability().available.amount("gpu.local") == Decimal("1")


def test_expiry_is_durable_idempotent_and_restores_capacity(postgres_dsn: str) -> None:
    _seed_resources(postgres_dsn)
    store = PostgresResourceReservationStore(postgres_dsn)
    expires_at = utcnow() + timedelta(minutes=5)
    reservation = store.reserve(
        ResourceReservationRequest(
            owner_type="experiment_contract",
            owner_id=uuid4(),
            idempotency_key="contract:expiring:reserve",
            requirements=ResourceVector(quantities={"cash.usd": Decimal("80")}),
            expires_at=expires_at,
        )
    )

    assert store.availability().available.amount("cash.usd") == Decimal("20")
    with pytest.raises(ReservationNotDueError):
        store.expire(reservation.id, as_of=expires_at - timedelta(seconds=1))

    expiry_time = expires_at + timedelta(seconds=1)
    assert store.expire_due(as_of=expiry_time) == 1
    assert store.expire_due(as_of=expiry_time) == 0

    expired = store.get(reservation.id)
    assert expired is not None
    assert expired.status is ResourceReservationStatus.RELEASED
    assert expired.expires_at == expires_at
    assert expired.expired_at == expiry_time
    assert expired.released_at == expiry_time
    assert store.expire(reservation.id, as_of=expiry_time) == expired
    assert store.release(reservation.id) == expired
    assert store.availability().available.amount("cash.usd") == Decimal("100")


def test_unknown_and_unavailable_resources_are_rejected(postgres_dsn: str) -> None:
    _seed_resources(postgres_dsn)
    world_store = PostgresStore(postgres_dsn)
    world_store.save_resource(
        Resource(
            name="human.operator_minutes",
            kind=ResourceKind.HUMAN,
            available=False,
            capacity=Decimal("60"),
            labels={"unit": "minutes"},
        )
    )
    store = PostgresResourceReservationStore(postgres_dsn)

    with pytest.raises(ResourceNotFoundError, match="missing.resource"):
        store.reserve(
            ResourceReservationRequest(
                owner_type="experiment_contract",
                owner_id=uuid4(),
                idempotency_key="missing:resource",
                requirements=ResourceVector(quantities={"missing.resource": 1}),
            )
        )

    with pytest.raises(ResourceUnavailableError, match="human.operator_minutes"):
        store.reserve(
            ResourceReservationRequest(
                owner_type="experiment_contract",
                owner_id=uuid4(),
                idempotency_key="unavailable:human",
                requirements=ResourceVector(
                    quantities={"human.operator_minutes": Decimal("5")}
                ),
            )
        )


def test_concurrent_reservations_cannot_overbook_one_resource(postgres_dsn: str) -> None:
    _seed_resources(postgres_dsn)
    barrier = Barrier(2)

    def attempt(index: int) -> bool:
        store = PostgresResourceReservationStore(postgres_dsn)
        barrier.wait()
        try:
            store.reserve(
                ResourceReservationRequest(
                    owner_type="experiment_contract",
                    owner_id=uuid4(),
                    idempotency_key=f"concurrent:{index}",
                    requirements=ResourceVector(
                        quantities={"cash.usd": Decimal("60")}
                    ),
                )
            )
        except ResourceCapacityError:
            return False
        return True

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(attempt, [1, 2]))

    assert sorted(results) == [False, True]
    snapshot = PostgresResourceReservationStore(postgres_dsn).availability(["cash.usd"])
    assert snapshot.reserved.amount("cash.usd") == Decimal("60")
    assert snapshot.available.amount("cash.usd") == Decimal("40")
