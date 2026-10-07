from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from business_master.domain.capital import (
    CapitalAuthorizationRequest,
    CapitalEnvelope,
    CapitalRequirement,
    CapitalStage,
    SpendCategory,
)
from business_master.domain.enums import EvidenceTier, RiskLevel
from business_master.domain.experiment_contracts import (
    ExperimentContract,
    MeasurementContract,
)
from business_master.domain.family_evaluation import (
    BusinessFamily,
    EvaluationRecommendation,
    FamilyEvaluation,
    ReadinessStatus,
)
from business_master.domain.portfolio import (
    PortfolioCandidate,
    PortfolioPlanRequest,
    PortfolioRole,
    PortfolioValueEstimate,
)
from business_master.domain.resources import ResourceAvailability, ResourceVector
from business_master.policies.capital import CapitalPolicy
from business_master.policies.portfolio import PortfolioPolicy

NOW = datetime(2026, 10, 7, 12, tzinfo=UTC)


def test_graduate_recommendation_does_not_imply_capital_authority() -> None:
    hypothesis_id = uuid4()
    contract = ExperimentContract(
        economic_hypothesis_id=hypothesis_id,
        business_family="content",
        question="Does this graduated opportunity merit a bounded paid probe?",
        expected_observation="External signal remains positive.",
        falsification_condition="External signal collapses.",
        measurement=MeasurementContract(
            window_seconds=3600,
            primary_metric="signal",
        ),
        resource_requirements=ResourceVector(),
    )
    evaluation = FamilyEvaluation(
        id=uuid4(),
        idempotency_key=f"graduate-boundary-{uuid4()}",
        family=BusinessFamily.CONTENT,
        hypothesis_id=hypothesis_id,
        contract_id=contract.id,
        belief_state_version=3,
        current_tier=EvidenceTier.PROBE,
        policy_name="family_evaluation:content",
        policy_version="2",
        evidence_ids=[],
        interpretations=[],
        criteria=[],
        external_observations=2,
        independent_sources=2,
        replication_count=2,
        distinct_contexts=1,
        evidence_sufficient=True,
        supporting_signal=True,
        falsified=False,
        economic_readiness=ReadinessStatus.UNKNOWN,
        operational_readiness=ReadinessStatus.READY,
        recommendation=EvaluationRecommendation.GRADUATE,
        rationale="Family evidence supports progression, not financial authority.",
        evaluated_at=NOW,
    )
    candidate = PortfolioCandidate(
        family_evaluation=evaluation,
        contract=contract,
        roles=(PortfolioRole.SIGNAL,),
        value=PortfolioValueEstimate(
            information_value=0.8,
            feedback_speed=0.8,
        ),
        capital_requirement=CapitalRequirement(
            amount=Decimal("25"),
            currency="USD",
            category=SpendCategory.PAID_ADS,
        ),
        group_key="graduate-paid-probe",
    )
    plan = PortfolioPolicy().plan(
        PortfolioPlanRequest(
            idempotency_key="graduate-does-not-authorize-cash",
            candidates=(candidate,),
            availability=ResourceAvailability(
                capacity=ResourceVector(),
                reserved=ResourceVector(),
                available=ResourceVector(),
            ),
            base_currency="USD",
            max_candidates=1,
            exploration_fraction=0.0,
            max_group_fraction=1.0,
            created_at=NOW,
        )
    )

    assert len(plan.allocations) == 1
    allocation = plan.allocations[0]
    assert allocation.recommendation is EvaluationRecommendation.GRADUATE
    assert allocation.capital_requirement is not None

    request = CapitalAuthorizationRequest(
        idempotency_key="graduate-capital-still-locked",
        portfolio_allocation_id=allocation.id,
        family_evaluation_id=allocation.family_evaluation_id,
        hypothesis_id=allocation.hypothesis_id,
        amount=allocation.capital_requirement.amount,
        currency=allocation.capital_requirement.currency,
        category=allocation.capital_requirement.category,
        stage=CapitalStage.LOCKED,
        risk=RiskLevel.LOW,
        requested_at=NOW,
        expires_at=NOW + timedelta(hours=1),
    )
    assessment = CapitalPolicy().assess(
        request,
        CapitalEnvelope(
            currency="USD",
            stage=CapitalStage.LOCKED,
            max_per_authorization=Decimal("1000000"),
            max_outstanding=Decimal("1000000"),
            max_risk=RiskLevel.CRITICAL,
        ),
        assessed_at=NOW,
        ledger_cash=Decimal("1000000"),
        active_outstanding=Decimal(0),
    )

    assert assessment.authorized is False
    assert "locked" in assessment.rationale.lower()
