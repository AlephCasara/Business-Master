from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from business_master.domain.enums import ResourceReservationStatus
from business_master.domain.resources import (
    ResourceReservation,
    ResourceReservationRequest,
    ResourceVector,
)


def test_resource_vector_preserves_non_fungible_dimensions() -> None:
    demand = ResourceVector(
        quantities={
            "cash.usd": Decimal("12.50"),
            "gpu.local": Decimal("1"),
            "human.operator_minutes": Decimal("0"),
        }
    )
    capacity = ResourceVector(
        quantities={
            "cash.usd": Decimal("20"),
            "gpu.local": Decimal("1"),
        }
    )

    assert demand.quantities == {
        "cash.usd": Decimal("12.50"),
        "gpu.local": Decimal("1"),
    }
    assert demand.amount("human.operator_minutes") == 0
    assert demand.fits_within(capacity)
    assert demand.plus(ResourceVector(quantities={"cash.usd": 2})).amount(
        "cash.usd"
    ) == Decimal("14.50")
    assert capacity.minus(demand).amount("cash.usd") == Decimal("7.50")


def test_resource_vector_rejects_invalid_quantities_and_keys() -> None:
    with pytest.raises(ValidationError, match="negative"):
        ResourceVector(quantities={"cash.usd": Decimal("-1")})

    with pytest.raises(ValidationError, match="finite"):
        ResourceVector(quantities={"gpu.local": Decimal("NaN")})

    with pytest.raises(ValidationError, match="trimmed"):
        ResourceVector(quantities={" cash.usd": Decimal("1")})


def test_reservation_request_requires_real_resource_demand() -> None:
    with pytest.raises(ValidationError, match="at least one positive quantity"):
        ResourceReservationRequest(
            owner_type="experiment_contract",
            owner_id=uuid4(),
            idempotency_key="experiment:test:resources",
            requirements=ResourceVector(),
        )


def test_released_reservation_requires_release_timestamp() -> None:
    with pytest.raises(ValidationError, match="released_at"):
        ResourceReservation(
            owner_type="experiment_contract",
            owner_id=uuid4(),
            idempotency_key="experiment:test:released",
            requirements=ResourceVector(quantities={"cash.usd": 1}),
            status=ResourceReservationStatus.RELEASED,
        )
