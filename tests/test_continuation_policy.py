from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from business_master.domain.capital import CapitalRequirement, SpendCategory
from business_master.domain.decisions import AutonomousContinuationRequest, ContinuationKind
from business_master.domain.enums import DecisionType, EvidenceTier, RiskLevel
from business_master.domain.family_evaluation import (
    BusinessFamily,
    EvaluationRecommendation,
    FamilyEvaluation,
    ReadinessStatus,
)
from business_master.domain.portfolio import (
    PortfolioAllocation,
    PortfolioRole,
    PortfolioValueEstimate,
    RiskAssessment,
)
from business_master.domain.resources import ResourceVector
from business_master.policies.continuation import (
    CapitalAuthorizationRequiredError,
    ContinuationPolicy,
    ContinuationPolicyError,
    HumanGateRequiredError,
)

NOW = datetime(2026, 10, 7, 9, tzinfo=UTC)


def _pair(
    recommendation: EvaluationRecommendation,
    *,
    tier: EvidenceTier = EvidenceTier.PROBE,
    risk: RiskAssessment | None = None,
    capital: CapitalRequirement | None = None,
) -> tuple[PortfolioAllocation, FamilyEvaluation]:
    hypothesis_id = uuid4()
    contract_id = uuid4()
    evaluation = FamilyEvaluation(
        id=uuid4(),
        idempotency_key=f"eval-{uuid4()}",
        family=BusinessFamily.CONTENT,
        hypothesis_id=hypothesis_id,
        contract_id=contract_id,
        belief_state_version=3,
        current_tier=tier,
        policy_name="family_evaluation:content",
        policy_version="2",
        evidence_ids=[uuid4()],
        interpretations=[],
        criteria=[],
        external_observations=1,
        independent_sources=1,
        replication_count=1,
        distinct_contexts=1,
        evidence_sufficient=True,
        supporting_signal=True,
        falsified=False,
        economic_readiness=ReadinessStatus.UNKNOWN,
        operational_readiness=ReadinessStatus.READY,
        recommendation=recommendation,
        rationale="persisted family evaluation rationale",
        evaluated_at=NOW,
    )
    allocation = PortfolioAllocation(
        id=uuid4(),
        candidate_id=uuid4(),
        family_evaluation_id=evaluation.id,
        hypothesis_id=hypothesis_id,
        contract_id=contract_id,
        belief_state_version=3,
        current_tier=tier,
        recommendation=recommendation,
        roles=(PortfolioRole.SIGNAL,),
        group_key="content-test",
        resource_demand=ResourceVector(
            quantities={"cpu.control": Decimal("0.25")}
        ),
        value=PortfolioValueEstimate(
            economic_value=0.3,
            information_value=0.8,
        ),
        risk=risk or RiskAssessment(level=RiskLevel.LOW),
        capital_requirement=capital,
        utility=0.7,
        scarcity_pressure=0.1,
        rationale="selected by portfolio",
    )
    return allocation, evaluation


def _request(allocation: PortfolioAllocation, *, key: str = "continuation") -> AutonomousContinuationRequest:
    return AutonomousContinuationRequest(
        idempotency_key=key,
        parent_experiment_id=uuid4(),
        portfolio_allocation_id=allocation.id,
        reservation_expires_at=NOW + timedelta(hours=1),
    )


@pytest.mark.parametrize(
    ("recommendation", "decision_type"),
    [
        (EvaluationRecommendation.INSUFFICIENT_EVIDENCE, DecisionType.CONTINUE),
        (EvaluationRecommendation.CONTINUE, DecisionType.CONTINUE),
        (EvaluationRecommendation.PAUSE, DecisionType.PAUSE),
        (EvaluationRecommendation.REJECT, DecisionType.KILL),
    ],
)
def test_non_child_recommendations_persist_decision_without_child(
    recommendation: EvaluationRecommendation,
    decision_type: DecisionType,
) -> None:
    allocation, evaluation = _pair(recommendation)
    request = _request(allocation, key=f"no-child-{recommendation.value}")

    decision = ContinuationPolicy().decide(
        request,
        allocation,
        evaluation,
        decided_at=NOW,
    )

    assert decision.decision_type is decision_type
    assert decision.continuation_kind is ContinuationKind.NONE
    assert decision.target_tier is None
    assert decision.child_experiment_id is None
    assert decision.child_contract_id is None
    assert decision.evidence_ids == evaluation.evidence_ids
    assert decision.reservation_expires_at == request.reservation_expires_at


def test_replicate_creates_same_tier_child_identity() -> None:
    allocation, evaluation = _pair(EvaluationRecommendation.REPLICATE)
    request = _request(allocation, key="replicate")

    decision = ContinuationPolicy().decide(
        request,
        allocation,
        evaluation,
        decided_at=NOW,
    )

    assert decision.decision_type is DecisionType.CONTINUE
    assert decision.continuation_kind is ContinuationKind.REPLICATE
    assert decision.target_tier is EvidenceTier.PROBE
    assert decision.child_experiment_id is not None
    assert decision.child_contract_id is not None
    assert decision.expected_resource_demand == allocation.resource_demand
    assert decision.risk == allocation.risk


def test_graduate_advances_exactly_one_tier() -> None:
    probe, probe_evaluation = _pair(EvaluationRecommendation.GRADUATE)
    pilot, pilot_evaluation = _pair(
        EvaluationRecommendation.GRADUATE,
        tier=EvidenceTier.PILOT,
    )

    probe_decision = ContinuationPolicy().decide(
        _request(probe, key="graduate-probe"),
        probe,
        probe_evaluation,
        decided_at=NOW,
    )
    pilot_decision = ContinuationPolicy().decide(
        _request(pilot, key="graduate-pilot"),
        pilot,
        pilot_evaluation,
        decided_at=NOW,
    )

    assert probe_decision.target_tier is EvidenceTier.PILOT
    assert pilot_decision.target_tier is EvidenceTier.SCALE
    assert probe_decision.decision_type is DecisionType.GRADUATE
    assert pilot_decision.decision_type is DecisionType.GRADUATE


def test_graduate_cannot_advance_beyond_scale() -> None:
    allocation, evaluation = _pair(
        EvaluationRecommendation.GRADUATE,
        tier=EvidenceTier.SCALE,
    )

    with pytest.raises(ContinuationPolicyError, match="cannot graduate"):
        ContinuationPolicy().decide(
            _request(allocation, key="graduate-scale"),
            allocation,
            evaluation,
            decided_at=NOW,
        )


def test_child_production_respects_human_gate() -> None:
    allocation, evaluation = _pair(
        EvaluationRecommendation.REPLICATE,
        risk=RiskAssessment(
            level=RiskLevel.MEDIUM,
            blast_radius=0.4,
            reversible=True,
            human_gate_required=True,
        ),
    )

    with pytest.raises(HumanGateRequiredError, match="human gate"):
        ContinuationPolicy().decide(
            _request(allocation, key="human-gate"),
            allocation,
            evaluation,
            decided_at=NOW,
        )


def test_capital_requirement_needs_active_authorization_for_child() -> None:
    capital = CapitalRequirement(
        amount=Decimal("25"),
        currency="USD",
        category=SpendCategory.PAID_ADS,
    )
    allocation, evaluation = _pair(
        EvaluationRecommendation.REPLICATE,
        capital=capital,
    )

    with pytest.raises(CapitalAuthorizationRequiredError, match="active PR9"):
        ContinuationPolicy().decide(
            _request(allocation, key="capital-gate"),
            allocation,
            evaluation,
            decided_at=NOW,
        )

    authorization_id = uuid4()
    decision = ContinuationPolicy().decide(
        _request(allocation, key="capital-authorized"),
        allocation,
        evaluation,
        decided_at=NOW,
        capital_authorization_id=authorization_id,
    )
    assert decision.capital_authorization_id == authorization_id
    assert decision.capital_requirement == capital


def test_policy_rejects_allocation_evaluation_lineage_drift() -> None:
    allocation, evaluation = _pair(EvaluationRecommendation.REPLICATE)
    drifted = evaluation.model_copy(update={"belief_state_version": 4})

    with pytest.raises(ContinuationPolicyError, match="belief-version"):
        ContinuationPolicy().decide(
            _request(allocation, key="lineage-drift"),
            allocation,
            drifted,
            decided_at=NOW,
        )
