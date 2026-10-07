from __future__ import annotations

from dataclasses import dataclass
from math import ceil, floor
from uuid import UUID

from business_master.domain.enums import EvidenceTier, RiskLevel
from business_master.domain.family_evaluation import EvaluationRecommendation
from business_master.domain.portfolio import (
    PortfolioAllocation,
    PortfolioCandidate,
    PortfolioCandidateEvaluation,
    PortfolioPlan,
    PortfolioPlanRequest,
    PortfolioRole,
)
from business_master.domain.resources import ResourceAvailability, ResourceVector

_RISK_ORDER: dict[RiskLevel, int] = {
    RiskLevel.ZERO: 0,
    RiskLevel.LOW: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
    RiskLevel.CRITICAL: 4,
}


@dataclass(frozen=True, slots=True)
class PortfolioPolicy:
    """Pure V2 constrained portfolio policy over bounded candidate actions."""

    name: str = "portfolio_control"
    version: str = "3"
    economic_weight: float = 0.30
    information_weight: float = 0.25
    option_weight: float = 0.10
    asset_weight: float = 0.15
    feedback_weight: float = 0.10
    uncertainty_weight: float = 0.10
    scarcity_penalty_weight: float = 0.30

    def plan(self, request: PortfolioPlanRequest) -> PortfolioPlan:
        evaluated = [
            self._evaluate_candidate(candidate, request)
            for candidate in request.candidates
        ]
        by_id = {item.candidate_id: item for item in evaluated}
        eligible = [
            candidate
            for candidate in request.candidates
            if by_id[candidate.id].eligible
        ]

        # Concentration is a hard ceiling. Never round upward: if the configured
        # share is too small to admit even one candidate, the cap is zero and the
        # caller must relax/replan explicitly rather than silently exceed policy.
        group_cap = floor(request.max_candidates * request.max_group_fraction)
        exploration_target = ceil(request.max_candidates * request.exploration_fraction)
        exploration_pool = [candidate for candidate in eligible if self._is_exploration(candidate)]
        exploration_target = min(exploration_target, len(exploration_pool))

        selected_ids: set[UUID] = set()
        allocations: list[PortfolioAllocation] = []
        group_counts: dict[str, int] = {}
        remaining = request.availability.available

        def try_select(candidate: PortfolioCandidate) -> bool:
            nonlocal remaining
            if candidate.id in selected_ids:
                return False
            if len(allocations) >= request.max_candidates:
                return False
            if group_counts.get(candidate.group_key, 0) >= group_cap:
                return False
            if not candidate.resource_demand.fits_within(remaining):
                return False

            evaluation = by_id[candidate.id]
            allocation = PortfolioAllocation(
                id=PortfolioAllocation.deterministic_id(
                    request.idempotency_key,
                    candidate.id,
                ),
                candidate_id=candidate.id,
                family_evaluation_id=candidate.family_evaluation.id,
                hypothesis_id=candidate.family_evaluation.hypothesis_id,
                contract_id=candidate.contract.id,
                belief_state_version=candidate.family_evaluation.belief_state_version,
                current_tier=candidate.current_tier,
                recommendation=candidate.recommendation,
                roles=candidate.roles,
                group_key=candidate.group_key,
                resource_demand=candidate.resource_demand,
                value=candidate.value,
                risk=candidate.risk,
                capital_requirement=candidate.capital_requirement,
                utility=evaluation.utility,
                scarcity_pressure=evaluation.scarcity_pressure,
                rationale=(
                    f"Selected by {self.name} v{self.version}; "
                    f"family recommendation={candidate.recommendation.value}; "
                    f"utility={evaluation.utility:.6f}; "
                    f"scarcity={evaluation.scarcity_pressure:.6f}."
                ),
            )
            allocations.append(allocation)
            selected_ids.add(candidate.id)
            group_counts[candidate.group_key] = group_counts.get(candidate.group_key, 0) + 1
            remaining = remaining.minus(candidate.resource_demand)
            return True

        ranked_exploration = sorted(
            exploration_pool,
            key=lambda candidate: (-by_id[candidate.id].utility, str(candidate.id)),
        )
        selected_exploration = 0
        for candidate in ranked_exploration:
            if selected_exploration >= exploration_target:
                break
            if try_select(candidate):
                selected_exploration += 1

        ranked_all = sorted(
            eligible,
            key=lambda candidate: (-by_id[candidate.id].utility, str(candidate.id)),
        )
        for candidate in ranked_all:
            if len(allocations) >= request.max_candidates:
                break
            try_select(candidate)

        final_evaluations = [
            item.model_copy(update={"selected": item.candidate_id in selected_ids})
            for item in evaluated
        ]

        return PortfolioPlan(
            id=PortfolioPlan.deterministic_id(request.idempotency_key),
            idempotency_key=request.idempotency_key,
            policy_name=self.name,
            policy_version=self.version,
            policy_parameters={
                "economic_weight": self.economic_weight,
                "information_weight": self.information_weight,
                "option_weight": self.option_weight,
                "asset_weight": self.asset_weight,
                "feedback_weight": self.feedback_weight,
                "uncertainty_weight": self.uncertainty_weight,
                "scarcity_penalty_weight": self.scarcity_penalty_weight,
                "base_currency": request.base_currency,
                "max_candidates": request.max_candidates,
                "exploration_fraction": request.exploration_fraction,
                "max_group_fraction": request.max_group_fraction,
                "max_risk": request.max_risk.value,
                "allow_human_gate": request.allow_human_gate,
            },
            base_currency=request.base_currency,
            available_resources=request.availability.available,
            evaluations=final_evaluations,
            allocations=allocations,
            created_at=request.created_at,
        )

    def _evaluate_candidate(
        self,
        candidate: PortfolioCandidate,
        request: PortfolioPlanRequest,
    ) -> PortfolioCandidateEvaluation:
        scarcity = self._scarcity_pressure(
            candidate.resource_demand,
            request.availability,
        )

        if candidate.recommendation in {
            EvaluationRecommendation.PAUSE,
            EvaluationRecommendation.REJECT,
        }:
            return PortfolioCandidateEvaluation(
                candidate_id=candidate.id,
                eligible=False,
                utility=0.0,
                scarcity_pressure=scarcity,
                rationale="Family evaluation blocks new allocation.",
            )

        if (
            candidate.recommendation is EvaluationRecommendation.INSUFFICIENT_EVIDENCE
            and PortfolioRole.SIGNAL not in candidate.roles
        ):
            return PortfolioCandidateEvaluation(
                candidate_id=candidate.id,
                eligible=False,
                utility=0.0,
                scarcity_pressure=scarcity,
                rationale="Insufficient evidence is eligible only for bounded signal work.",
            )

        if _RISK_ORDER[candidate.risk.level] > _RISK_ORDER[request.max_risk]:
            return PortfolioCandidateEvaluation(
                candidate_id=candidate.id,
                eligible=False,
                utility=0.0,
                scarcity_pressure=scarcity,
                rationale="Candidate risk exceeds portfolio policy limit.",
            )

        if candidate.risk.human_gate_required and not request.allow_human_gate:
            return PortfolioCandidateEvaluation(
                candidate_id=candidate.id,
                eligible=False,
                utility=0.0,
                scarcity_pressure=scarcity,
                rationale="Candidate requires a human gate that this plan does not admit.",
            )

        if not candidate.resource_demand.fits_within(request.availability.available):
            return PortfolioCandidateEvaluation(
                candidate_id=candidate.id,
                eligible=False,
                utility=0.0,
                scarcity_pressure=scarcity,
                rationale="Candidate resource demand does not fit current availability.",
            )

        if (
            candidate.capital_requirement is not None
            and candidate.capital_requirement.currency != request.base_currency
        ):
            return PortfolioCandidateEvaluation(
                candidate_id=candidate.id,
                eligible=False,
                utility=0.0,
                scarcity_pressure=scarcity,
                rationale=(
                    "Capital requirement currency differs from portfolio base currency; "
                    "explicit valuation/FX evidence is required."
                ),
            )

        if (
            candidate.value.expected_value_currency is not None
            and candidate.value.expected_value_currency != request.base_currency
        ):
            return PortfolioCandidateEvaluation(
                candidate_id=candidate.id,
                eligible=False,
                utility=0.0,
                scarcity_pressure=scarcity,
                rationale=(
                    "Expected monetary value currency differs from portfolio base currency; "
                    "implicit FX is forbidden."
                ),
            )

        value = candidate.value
        uncertainty_effect = (
            self.uncertainty_weight * value.uncertainty
            if candidate.current_tier is EvidenceTier.PROBE
            else -self.uncertainty_weight * value.uncertainty
        )
        utility = (
            self.economic_weight * value.economic_value
            + self.information_weight * value.information_value
            + self.option_weight * value.option_value
            + self.asset_weight * value.asset_value
            + self.feedback_weight * value.feedback_speed
            + uncertainty_effect
            - self.scarcity_penalty_weight * scarcity
        )
        return PortfolioCandidateEvaluation(
            candidate_id=candidate.id,
            eligible=True,
            utility=utility,
            scarcity_pressure=scarcity,
            rationale=(
                "Candidate clears family, currency, risk, human-gate, "
                "and resource feasibility gates."
            ),
        )

    @staticmethod
    def _scarcity_pressure(
        demand: ResourceVector,
        availability: ResourceAvailability,
    ) -> float:
        """Return non-monetary pressure for resources the candidate would consume.

        Existing reservation pressure and the candidate's marginal claim both matter.
        Hard feasibility is enforced separately and can never be bypassed by scoring.
        """

        if not demand.quantities:
            return 0.0
        pressures: list[float] = []
        for name, amount in demand.quantities.items():
            capacity = availability.capacity.amount(name)
            free = availability.available.amount(name)
            reserved = availability.reserved.amount(name)
            if capacity <= 0 or free <= 0:
                return 1.0
            reservation_pressure = min(float(reserved / capacity), 1.0)
            marginal_pressure = min(float(amount / free), 1.0)
            pressures.append(max(reservation_pressure, marginal_pressure))
        return max(pressures, default=0.0)

    @staticmethod
    def _is_exploration(candidate: PortfolioCandidate) -> bool:
        return (
            candidate.current_tier is EvidenceTier.PROBE
            or PortfolioRole.SIGNAL in candidate.roles
        )
