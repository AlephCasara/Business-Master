from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from business_master.domain.capital import (
    CapitalAssessment,
    CapitalAuthorizationRequest,
    CapitalEnvelope,
    CapitalStage,
)
from business_master.domain.enums import RiskLevel

_RISK_ORDER: dict[RiskLevel, int] = {
    RiskLevel.ZERO: 0,
    RiskLevel.LOW: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
    RiskLevel.CRITICAL: 4,
}


@dataclass(frozen=True, slots=True)
class CapitalPolicy:
    """Pure bounded capital-admission policy; it never moves money."""

    name: str = "capital_control"
    version: str = "1"

    def assess(
        self,
        request: CapitalAuthorizationRequest,
        envelope: CapitalEnvelope,
        *,
        ledger_cash: Decimal,
        active_outstanding: Decimal,
        period_committed: Decimal = Decimal(0),
    ) -> CapitalAssessment:
        authorizable_cash = max(ledger_cash - active_outstanding, Decimal(0))

        def denied(reason: str) -> CapitalAssessment:
            return CapitalAssessment(
                authorized=False,
                ledger_cash=ledger_cash,
                active_outstanding=active_outstanding,
                period_committed=period_committed,
                authorizable_cash=authorizable_cash,
                rationale=reason,
            )

        if request.currency != envelope.currency:
            return denied("Capital request currency does not match the envelope currency.")
        if request.stage is not envelope.stage:
            return denied("Capital request stage does not match the active envelope stage.")
        if envelope.stage is CapitalStage.LOCKED:
            return denied("Capital envelope is locked; paid authorization is disabled.")
        if _RISK_ORDER[request.risk] > _RISK_ORDER[envelope.max_risk]:
            return denied("Requested risk exceeds the capital envelope risk limit.")
        if request.amount > envelope.max_per_authorization:
            return denied("Requested amount exceeds max_per_authorization.")
        if active_outstanding + request.amount > envelope.max_outstanding:
            return denied("Requested amount exceeds max_outstanding after active commitments.")
        if request.amount > authorizable_cash:
            return denied("Requested amount exceeds ledger cash net of active authorizations.")

        if envelope.operator_hard_ceiling is not None:
            if envelope.period_start is None or envelope.period_end is None:
                return denied("Operator hard ceiling requires an explicit control period.")
            if not (envelope.period_start <= request.requested_at < envelope.period_end):
                return denied("Capital request is outside the operator control period.")
            if request.expires_at is None or request.expires_at > envelope.period_end:
                return denied(
                    "Authorization under a period ceiling must expire within that period."
                )
            if period_committed + request.amount > envelope.operator_hard_ceiling:
                return denied("Requested amount exceeds the operator hard ceiling for the period.")

        return CapitalAssessment(
            authorized=True,
            ledger_cash=ledger_cash,
            active_outstanding=active_outstanding,
            period_committed=period_committed,
            authorizable_cash=authorizable_cash,
            rationale=(
                "Request fits ledger cash, active commitments, envelope limits, "
                "operator ceiling, and risk policy."
            ),
        )
