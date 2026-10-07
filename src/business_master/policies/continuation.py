from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from business_master.domain.decisions import (
    AutonomousContinuationRequest,
    AutonomousDecision,
    ContinuationKind,
)
from business_master.domain.enums import DecisionType, EvidenceTier
from business_master.domain.family_evaluation import (
    EvaluationRecommendation,
    FamilyEvaluation,
)
from business_master.domain.portfolio import PortfolioAllocation


class ContinuationPolicyError(RuntimeError):
    """Base error for invalid deterministic continuation state."""


class HumanGateRequiredError(ContinuationPolicyError):
    """Raised when a child-producing allocation still requires a human gate."""


class CapitalAuthorizationRequiredError(ContinuationPolicyError):
    """Raised when a capital-requiring child lacks active PR9 authorization."""


@dataclass(frozen=True, slots=True)
class ContinuationPolicy:
    name: str = "autonomous_continuation"
    version: str = "1"

    def decide(
        self,
        request: AutonomousContinuationRequest,
        allocation: PortfolioAllocation,
        evaluation: FamilyEvaluation,
        *,
        decided_at: datetime,
        capital_authorization_id: UUID | None = None,
    ) -> AutonomousDecision:
        self._validate_lineage(allocation, evaluation)
        if decided_at.tzinfo is None or decided_at.utcoffset() is None:
            raise ValueError("decided_at must be timezone-aware")

        recommendation = evaluation.recommendation
        decision_type, continuation_kind, target_tier = self._map_recommendation(
            recommendation,
            allocation.current_tier,
        )
        creates_child = continuation_kind is not ContinuationKind.NONE

        if creates_child and allocation.risk.human_gate_required:
            raise HumanGateRequiredError(
                "portfolio allocation requires a human gate before child materialization"
            )
        if (
            creates_child
            and allocation.capital_requirement is not None
            and capital_authorization_id is None
        ):
            raise CapitalAuthorizationRequiredError(
                "capital-requiring allocation needs an active PR9 authorization"
            )

        decision_id = AutonomousDecision.deterministic_id(request.idempotency_key)
        child_experiment_id = (
            AutonomousDecision.deterministic_child_experiment_id(decision_id)
            if creates_child
            else None
        )
        child_contract_id = (
            AutonomousDecision.deterministic_child_contract_id(decision_id)
            if creates_child
            else None
        )

        observed_features = {
            "family": evaluation.family.value,
            "recommendation": recommendation.value,
            "current_tier": allocation.current_tier.value,
            "evidence_sufficient": evaluation.evidence_sufficient,
            "supporting_signal": evaluation.supporting_signal,
            "falsified": evaluation.falsified,
            "external_observations": evaluation.external_observations,
            "independent_sources": evaluation.independent_sources,
            "replication_count": evaluation.replication_count,
            "distinct_contexts": evaluation.distinct_contexts,
            "utility": allocation.utility,
            "scarcity_pressure": allocation.scarcity_pressure,
            "roles": [role.value for role in allocation.roles],
        }
        rationale = (
            f"Family evaluation {evaluation.id} recommended {recommendation.value}. "
            f"PR10 policy chose {decision_type.value}/{continuation_kind.value}. "
            f"{evaluation.rationale}"
        )

        return AutonomousDecision(
            id=decision_id,
            idempotency_key=request.idempotency_key,
            parent_experiment_id=request.parent_experiment_id,
            portfolio_allocation_id=allocation.id,
            family_evaluation_id=evaluation.id,
            hypothesis_id=allocation.hypothesis_id,
            source_contract_id=allocation.contract_id,
            belief_state_version=allocation.belief_state_version,
            decision_type=decision_type,
            continuation_kind=continuation_kind,
            target_tier=target_tier,
            policy_name=self.name,
            policy_version=self.version,
            evidence_ids=list(evaluation.evidence_ids),
            observed_features=observed_features,
            expected_resource_demand=allocation.resource_demand,
            capital_requirement=allocation.capital_requirement,
            risk=allocation.risk,
            rationale=rationale,
            reservation_expires_at=request.reservation_expires_at,
            child_experiment_id=child_experiment_id,
            child_contract_id=child_contract_id,
            capital_authorization_id=capital_authorization_id,
            created_at=decided_at,
        )

    @staticmethod
    def _validate_lineage(
        allocation: PortfolioAllocation,
        evaluation: FamilyEvaluation,
    ) -> None:
        if allocation.family_evaluation_id != evaluation.id:
            raise ContinuationPolicyError("allocation family evaluation lineage is inconsistent")
        if allocation.hypothesis_id != evaluation.hypothesis_id:
            raise ContinuationPolicyError("allocation hypothesis lineage is inconsistent")
        if allocation.contract_id != evaluation.contract_id:
            raise ContinuationPolicyError("allocation contract lineage is inconsistent")
        if allocation.belief_state_version != evaluation.belief_state_version:
            raise ContinuationPolicyError("allocation belief-version lineage is inconsistent")
        if allocation.current_tier is not evaluation.current_tier:
            raise ContinuationPolicyError("allocation tier lineage is inconsistent")
        if allocation.recommendation is not evaluation.recommendation:
            raise ContinuationPolicyError("allocation recommendation lineage is inconsistent")

    @staticmethod
    def _map_recommendation(
        recommendation: EvaluationRecommendation,
        current_tier: EvidenceTier,
    ) -> tuple[DecisionType, ContinuationKind, EvidenceTier | None]:
        if recommendation is EvaluationRecommendation.REJECT:
            return DecisionType.KILL, ContinuationKind.NONE, None
        if recommendation is EvaluationRecommendation.PAUSE:
            return DecisionType.PAUSE, ContinuationKind.NONE, None
        if recommendation in {
            EvaluationRecommendation.INSUFFICIENT_EVIDENCE,
            EvaluationRecommendation.CONTINUE,
        }:
            return DecisionType.CONTINUE, ContinuationKind.NONE, None
        if recommendation is EvaluationRecommendation.REPLICATE:
            if current_tier in {EvidenceTier.PAUSED, EvidenceTier.KILLED}:
                raise ContinuationPolicyError(
                    "paused or killed evidence tier cannot create a replication child"
                )
            return DecisionType.CONTINUE, ContinuationKind.REPLICATE, current_tier
        if recommendation is EvaluationRecommendation.GRADUATE:
            if current_tier is EvidenceTier.PROBE:
                return DecisionType.GRADUATE, ContinuationKind.GRADUATE, EvidenceTier.PILOT
            if current_tier is EvidenceTier.PILOT:
                return DecisionType.GRADUATE, ContinuationKind.GRADUATE, EvidenceTier.SCALE
            raise ContinuationPolicyError(
                f"cannot graduate evidence tier {current_tier.value}"
            )
        raise ContinuationPolicyError(f"unsupported recommendation: {recommendation.value}")
