from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest

from business_master.domain.enums import ResourceKind
from business_master.domain.resources import (
    Resource,
    ResourceReservationRequest,
    ResourceUsageRequest,
    ResourceVector,
)
from business_master.storage.postgres import PostgresStore
from business_master.storage.resource_reservations_postgres import (
    PostgresResourceReservationStore,
    ResourceNotFoundError,
)
from business_master.storage.resource_usage_postgres import (
    PostgresResourceUsageStore,
    ResourceUsageConflictError,
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
    world_store = PostgresStore(dsn)
    world_store.save_resource(
        Resource(
            name="gpu.seconds",
            kind=ResourceKind.GPU,
            capacity=Decimal("1000"),
            labels={"unit": "seconds"},
        )
    )
    world_store.save_resource(
        Resource(
            name="llm.tokens",
            kind=ResourceKind.LLM,
            capacity=Decimal("100000"),
            labels={"unit": "tokens"},
        )
    )


def test_actual_usage_is_separate_from_reserved_capacity(postgres_dsn: str) -> None:
    _seed_resources(postgres_dsn)
    reservation_store = PostgresResourceReservationStore(postgres_dsn)
    usage_store = PostgresResourceUsageStore(postgres_dsn)
    reservation = reservation_store.reserve(
        ResourceReservationRequest(
            owner_type="experiment_contract",
            owner_id=uuid4(),
            idempotency_key="usage:reservation",
            requirements=ResourceVector(quantities={"gpu.seconds": Decimal("100")}),
        )
    )

    request = ResourceUsageRequest(
        reservation_id=reservation.id,
        execution_id=uuid4(),
        idempotency_key="usage:observed:1",
        actual=ResourceVector(
            quantities={
                "gpu.seconds": Decimal("125"),
                "llm.tokens": Decimal("900"),
            }
        ),
    )
    first = usage_store.record(request)
    duplicate = usage_store.record(request)

    assert duplicate.id == first.id
    assert first.actual.amount("gpu.seconds") == Decimal("125")
    assert first.actual.amount("llm.tokens") == Decimal("900")

    snapshot = reservation_store.availability(["gpu.seconds", "llm.tokens"])
    assert snapshot.reserved.amount("gpu.seconds") == Decimal("100")
    assert snapshot.reserved.amount("llm.tokens") == Decimal("0")
    assert snapshot.available.amount("gpu.seconds") == Decimal("900")
    assert snapshot.available.amount("llm.tokens") == Decimal("100000")

    reservation_store.release(reservation.id)
    persisted = usage_store.list_for_reservation(reservation.id)
    assert persisted == [first]
    assert reservation_store.availability(["gpu.seconds"]).available.amount(
        "gpu.seconds"
    ) == Decimal("1000")


def test_usage_idempotency_conflict_and_unknown_dimensions_are_rejected(
    postgres_dsn: str,
) -> None:
    _seed_resources(postgres_dsn)
    reservation = PostgresResourceReservationStore(postgres_dsn).reserve(
        ResourceReservationRequest(
            owner_type="experiment_contract",
            owner_id=uuid4(),
            idempotency_key="usage:reservation:2",
            requirements=ResourceVector(quantities={"gpu.seconds": Decimal("50")}),
        )
    )
    usage_store = PostgresResourceUsageStore(postgres_dsn)
    request = ResourceUsageRequest(
        reservation_id=reservation.id,
        idempotency_key="usage:observed:2",
        actual=ResourceVector(quantities={"gpu.seconds": Decimal("40")}),
    )
    usage_store.record(request)

    with pytest.raises(ResourceUsageConflictError, match="idempotency key"):
        usage_store.record(
            ResourceUsageRequest(
                reservation_id=reservation.id,
                idempotency_key=request.idempotency_key,
                actual=ResourceVector(quantities={"gpu.seconds": Decimal("41")}),
            )
        )

    with pytest.raises(ResourceNotFoundError, match="unknown.resource"):
        usage_store.record(
            ResourceUsageRequest(
                reservation_id=reservation.id,
                idempotency_key="usage:unknown",
                actual=ResourceVector(quantities={"unknown.resource": Decimal("1")}),
            )
        )
