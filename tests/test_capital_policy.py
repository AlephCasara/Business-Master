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
        requested_at=NOW,
        expires_at=NOW + timedelta(hours=1),
    )


def _envelope(
    *,
    max_per: str = "100",
    max_outstanding: str = "100",
    hard_ceiling: str | None = None,
    max_risk: RiskLevel = RiskLevel.MEDIUM,
    stage: CapitalStage = CapitalStage.PROBE,
) -> CapitalEnvelope:
    return CapitalEnvelope(
        currency="USD",
        stage=stage,
        max_per_authorization=Decimal(max_per),
        max_outstanding=Decimal(max_outstanding),
        max_risk=max_risk,
        operator_hard_ceiling=None if hard_ceiling is None else Decimal(hard_ceiling),
        period_start=None if hard_ceiling is None else NOW.replace(hour=0),
        period_end=None if hard_ceiling is None else NOW.replace(hour=0) + timedelta(days=1),
    )


def test_locked_envelope_never_authorizes_paid_capital() -> None:
    assessment = CapitalPolicy().assess(
        _request(stage=CapitalStage.LOCKED),
        _envelope(stage=CapitalStage.LOCKED),
        ledger_cash=Decimal("1000"),
        active_outstanding=Decimal(0),
    )

    assert assessment.authorized is False
    assert "locked" in assessment.rationale.lower()


def test_ledger_cash_is_reduced_by_active_authorizations() -> None:
    assessment = CapitalPolicy().assess(
        _request(amount="60"),
        _envelope(max_outstanding="100"),
        ledger_cash=Decimal("100"),
        active_outstanding=Decimal("50"),
    )

    assert assessment.authorized is False
    assert assessment.authorizable_cash == Decimal("50")
    assert "ledger cash" in assessment.rationale.lower()


def test_operator_zero_ceiling_blocks_otherwise_affordable_spend() -> None:
    assessment = CapitalPolicy().assess(
        _request(amount="10"),
        _envelope(hard_ceiling="0"),
        ledger_cash=Decimal("1000"),
        active_outstanding=Decimal(0),
        period_committed=Decimal(0),
    )

    assert assessment.authorized is False
    assert "operator hard ceiling" in assessment.rationale.lower()


def test_operator_ceiling_can_be_stricter_than_ledger_cash() -> None:
    assessment = CapitalPolicy().assess(
        _request(amount="30"),
        _envelope(hard_ceiling="50"),
        ledger_cash=Decimal("1000"),
        active_outstanding=Decimal(0),
        period_committed=Decimal("25"),
    )

    assert assessment.authorized is False
    assert "operator hard ceiling" in assessment.rationale.lower()


def test_risk_limit_is_deterministic() -> None:
    assessment = CapitalPolicy().assess(
        _request(risk=RiskLevel.HIGH),
        _envelope(max_risk=RiskLevel.MEDIUM),
        ledger_cash=Decimal("1000"),
        active_outstanding=Decimal(0),
    )

    assert assessment.authorized is False
    assert "risk" in assessment.rationale.lower()


def test_valid_request_is_authorized_without_moving_money() -> None:
    assessment = CapitalPolicy().assess(
        _request(amount="25"),
        _envelope(hard_ceiling="100"),
        ledger_cash=Decimal("100"),
        active_outstanding=Decimal("20"),
        period_committed=Decimal("10"),
    )

    assert assessment.authorized is True
    assert assessment.authorizable_cash == Decimal("80")
