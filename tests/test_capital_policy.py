from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from business_master.domain.capital import (
    CapitalAuthorizationRequest,
    CapitalEnvelope,
    CapitalStage,
    SpendCategory,
)
from business_master.domain.enums import RiskLevel
from business_master.policies.capital import CapitalPolicy

NOW = datetime(2026, 10, 7, 12, tzinfo=UTC)


def _request(
    *,
    amount: str = "25",
    currency: str = "USD",
    risk: RiskLevel = RiskLevel.LOW,
    stage: CapitalStage = CapitalStage.PROBE,
    requested_at: datetime = NOW,
    expires_at: datetime | None = None,
) -> CapitalAuthorizationRequest:
    return CapitalAuthorizationRequest(
        idempotency_key=f"capital-{uuid4()}",
        portfolio_allocation_id=uuid4(),
        family_evaluation_id=uuid4(),
        hypothesis_id=uuid4(),
        amount=Decimal(amount),
        currency=currency,
        category=SpendCategory.PAID_ADS,
        stage=stage,
        risk=risk,
        requested_at=requested_at,
        expires_at=expires_at or requested_at + timedelta(hours=1),
    )


def _envelope(
    *,
    max_per: str = "100",
    max_outstanding: str = "100",
    hard_ceiling: str | None = None,
    max_risk: RiskLevel = RiskLevel.MEDIUM,
    stage: CapitalStage = CapitalStage.PROBE,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
) -> CapitalEnvelope:
    default_start = NOW.replace(hour=0)
    default_end = default_start + timedelta(days=1)
    return CapitalEnvelope(
        currency="USD",
        stage=stage,
        max_per_authorization=Decimal(max_per),
        max_outstanding=Decimal(max_outstanding),
        max_risk=max_risk,
        operator_hard_ceiling=None if hard_ceiling is None else Decimal(hard_ceiling),
        period_start=None if hard_ceiling is None else period_start or default_start,
        period_end=None if hard_ceiling is None else period_end or default_end,
    )


def _assess(
    request: CapitalAuthorizationRequest,
    envelope: CapitalEnvelope,
    *,
    assessed_at: datetime = NOW,
    ledger_cash: Decimal = Decimal("1000"),
    active_outstanding: Decimal = Decimal(0),
    period_committed: Decimal = Decimal(0),
):
    return CapitalPolicy().assess(
        request,
        envelope,
        assessed_at=assessed_at,
        ledger_cash=ledger_cash,
        active_outstanding=active_outstanding,
        period_committed=period_committed,
    )


def test_locked_envelope_never_authorizes_paid_capital() -> None:
    assessment = _assess(
        _request(stage=CapitalStage.LOCKED),
        _envelope(stage=CapitalStage.LOCKED),
    )

    assert assessment.authorized is False
    assert "locked" in assessment.rationale.lower()


def test_ledger_cash_is_reduced_by_active_authorizations() -> None:
    assessment = _assess(
        _request(amount="60"),
        _envelope(max_outstanding="100"),
        ledger_cash=Decimal("100"),
        active_outstanding=Decimal("50"),
    )

    assert assessment.authorized is False
    assert assessment.authorizable_cash == Decimal("50")
    assert "ledger cash" in assessment.rationale.lower()


def test_operator_zero_ceiling_blocks_otherwise_affordable_spend() -> None:
    assessment = _assess(
        _request(amount="10"),
        _envelope(hard_ceiling="0"),
    )

    assert assessment.authorized is False
    assert "operator hard ceiling" in assessment.rationale.lower()


def test_operator_ceiling_can_be_stricter_than_ledger_cash() -> None:
    assessment = _assess(
        _request(amount="30"),
        _envelope(hard_ceiling="50"),
        period_committed=Decimal("25"),
    )

    assert assessment.authorized is False
    assert "operator hard ceiling" in assessment.rationale.lower()


def test_operator_period_uses_trusted_assessment_time_not_request_time() -> None:
    stale_request_time = NOW - timedelta(days=1)
    envelope = _envelope(
        hard_ceiling="100",
        period_start=NOW - timedelta(minutes=5),
        period_end=NOW + timedelta(hours=2),
    )
    request = _request(
        requested_at=stale_request_time,
        expires_at=NOW + timedelta(hours=1),
    )

    assessment = _assess(request, envelope, assessed_at=NOW)

    assert assessment.authorized is True


def test_stale_expiry_is_denied_at_trusted_assessment_time() -> None:
    request = _request(
        requested_at=NOW - timedelta(hours=2),
        expires_at=NOW - timedelta(minutes=1),
    )

    assessment = _assess(request, _envelope(), assessed_at=NOW)

    assert assessment.authorized is False
    assert "already expired" in assessment.rationale.lower()


def test_risk_limit_is_deterministic() -> None:
    assessment = _assess(
        _request(risk=RiskLevel.HIGH),
        _envelope(max_risk=RiskLevel.MEDIUM),
    )

    assert assessment.authorized is False
    assert "risk" in assessment.rationale.lower()


def test_valid_request_is_authorized_without_moving_money() -> None:
    assessment = _assess(
        _request(amount="25"),
        _envelope(hard_ceiling="100"),
        ledger_cash=Decimal("100"),
        active_outstanding=Decimal("20"),
        period_committed=Decimal("10"),
    )

    assert assessment.authorized is True
    assert assessment.authorizable_cash == Decimal("80")
