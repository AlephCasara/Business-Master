from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from business_master.domain.enums import (
    ComparisonOperator,
    EvidenceClass,
    EvidenceTier,
    MetricAggregation,
)
from business_master.domain.experiment_contracts import (
    ExperimentContract,
    MeasurementContract,
    MetricCriterion,
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
from business_master.policies.portfolio import PortfolioPolicy

NOW = datetime(2026, 10, 7, tzinfo=UTC)


def _contract(hypothesis_id: object, demand: ResourceVector) -> ExperimentContract:
    return ExperimentContract(
        economic_hypothesis_id=hypothesis_id,
        business_family="content",
        question="Does this bounded candidate produce useful evidence?",
        expected_observation="The signal metric clears threshold.",
        falsification_condition="The signal metric remains below threshold.",
        measurement=MeasurementContract(
            window_seconds=3600,
            primary_metric="signal",
            supporting_criteria=[
                MetricCriterion(
                    metric="signal",
                    operator=ComparisonOperator.GTE,
                    threshold=1.0,
                    evidence_class=EvidenceClass.MARKET,
                    aggregation=MetricAggregation.SUM,
                )
            ],
        ),
        resource_requirements=demand,
    )


def _evaluation(
    contract: ExperimentContract,
    *,
    recommendation: EvaluationRecommendation,
    tier: EvidenceTier = EvidenceTier.PROBE,
) -> FamilyEvaluation:
    return FamilyEvaluation(
        id=uuid4(),
        idempotency_key=f"eval-{uuid4()}",
        family=BusinessFamily.CONTENT,
        hypothesis_id=contract.economic_hypothesis_id,
        contract_id=contract.id,
        belief_state_version=2,
        current_tier=tier,
        policy_name="family_evaluation:content",
        policy_version="1",
        evidence_ids=[],
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
        rationale="test evaluation",
        evaluated_at=NOW,
    )


def _candidate(
    *,
    recommendation: EvaluationRecommendation = EvaluationRecommendation.REPLICATE,
    tier: EvidenceTier = EvidenceTier.PROBE,
    roles: tuple[PortfolioRole, ...] = (PortfolioRole.SIGNAL,),
    demand: ResourceVector | None = None,
    group_key: str = "group-a",
    economic: float = 0.2,
    information: float = 0.8,
) -> PortfolioCandidate:
    contract = _contract(
        uuid4(),
        demand or ResourceVector(quantities={"gpu.local": Decimal("0.1")}),
    )
    return PortfolioCandidate(
        family_evaluation=_evaluation(contract, recommendation=recommendation, tier=tier),
        contract=contract,
        roles=roles,
        value=PortfolioValueEstimate(
            economic_value=economic,
            information_value=information,
            feedback_speed=0.8,
            uncertainty=0.5,
        ),
        group_key=group_key,
    )


def _availability(**quantities: Decimal) -> ResourceAvailability:
    vector = ResourceVector(quantities=quantities)
    return ResourceAvailability(
        capacity=vector,
        reserved=ResourceVector(),
        available=vector,
    )


def test_candidate_rejects_mismatched_family_evaluation_lineage() -> None:
    contract = _contract(uuid4(), ResourceVector())
    different_contract = _contract(contract.economic_hypothesis_id, ResourceVector())
    evaluation = _evaluation(different_contract, recommendation=EvaluationRecommendation.CONTINUE)

    with pytest.raises(ValueError, match="contract does not match"):
        PortfolioCandidate(
            family_evaluation=evaluation,
            contract=contract,
            roles=(PortfolioRole.SIGNAL,),
            group_key="mismatch",
        )


def test_pause_reject_and_non_signal_insufficient_evidence_are_ineligible() -> None:
    candidates = (
        _candidate(recommendation=EvaluationRecommendation.PAUSE, group_key="pause"),
        _candidate(recommendation=EvaluationRecommendation.REJECT, group_key="reject"),
        _candidate(
            recommendation=EvaluationRecommendation.INSUFFICIENT_EVIDENCE,
            roles=(PortfolioRole.CASH,),
            group_key="insufficient-cash",
        ),
        _candidate(
            recommendation=EvaluationRecommendation.INSUFFICIENT_EVIDENCE,
            roles=(PortfolioRole.SIGNAL,),
            group_key="insufficient-signal",
        ),
    )
    plan = PortfolioPolicy().plan(
        PortfolioPlanRequest(
            idempotency_key="eligibility",
            candidates=candidates,
            availability=_availability(**{"gpu.local": Decimal("1")}),
            max_candidates=4,
        )
    )

    assert [allocation.candidate_id for allocation in plan.allocations] == [candidates[3].id]
    eligibility = {item.candidate_id: item.eligible for item in plan.evaluations}
    assert eligibility[candidates[0].id] is False
    assert eligibility[candidates[1].id] is False
    assert eligibility[candidates[2].id] is False
    assert eligibility[candidates[3].id] is True


def test_plan_never_exceeds_multidimensional_availability() -> None:
    candidates = tuple(
        _candidate(
            demand=ResourceVector(
                quantities={
                    "gpu.local": Decimal("0.6"),
                    "human.operator_minutes": Decimal("4"),
                }
            ),
            group_key=f"group-{index}",
        )
        for index in range(3)
    )
    plan = PortfolioPolicy().plan(
        PortfolioPlanRequest(
            idempotency_key="resource-fit",
            candidates=candidates,
            availability=_availability(
                **{
                    "gpu.local": Decimal("1"),
                    "human.operator_minutes": Decimal("10"),
                }
            ),
            max_candidates=3,
        )
    )

    assert len(plan.allocations) == 1
    aggregate = ResourceVector()
    for allocation in plan.allocations:
        aggregate = aggregate.plus(allocation.resource_demand)
    assert aggregate.fits_within(plan.available_resources)


def test_scarcity_penalty_prefers_less_constrained_candidate() -> None:
    scarce = _candidate(
        demand=ResourceVector(quantities={"gpu.local": Decimal("0.9")}),
        group_key="scarce",
    )
    light = _candidate(
        demand=ResourceVector(quantities={"gpu.local": Decimal("0.1")}),
        group_key="light",
    )
    plan = PortfolioPolicy().plan(
        PortfolioPlanRequest(
            idempotency_key="scarcity",
            candidates=(scarce, light),
            availability=_availability(**{"gpu.local": Decimal("1")}),
            max_candidates=1,
            exploration_fraction=0.0,
        )
    )

    assert plan.allocations[0].candidate_id == light.id
    evaluations = {item.candidate_id: item for item in plan.evaluations}
    assert evaluations[light.id].scarcity_pressure < evaluations[scarce.id].scarcity_pressure


def test_exploration_floor_can_override_higher_exploitation_utility() -> None:
    probe = _candidate(
        tier=EvidenceTier.PROBE,
        roles=(PortfolioRole.SIGNAL,),
        group_key="probe",
        economic=0.0,
        information=0.2,
    )
    mature = _candidate(
        tier=EvidenceTier.PILOT,
        roles=(PortfolioRole.CASH,),
        group_key="mature",
        economic=1.0,
        information=1.0,
    )
    plan = PortfolioPolicy().plan(
        PortfolioPlanRequest(
            idempotency_key="exploration-floor",
            candidates=(mature, probe),
            availability=_availability(**{"gpu.local": Decimal("1")}),
            max_candidates=1,
            exploration_fraction=1.0,
        )
    )

    assert plan.allocations[0].candidate_id == probe.id


def test_concentration_cap_limits_one_group() -> None:
    same_group = tuple(
        _candidate(group_key="dominant", economic=1.0, information=1.0)
        for _ in range(3)
    )
    diversifiers = tuple(
        _candidate(group_key=f"other-{index}", economic=0.2, information=0.2)
        for index in range(2)
    )
    plan = PortfolioPolicy().plan(
        PortfolioPlanRequest(
            idempotency_key="concentration",
            candidates=(*same_group, *diversifiers),
            availability=_availability(**{"gpu.local": Decimal("2")}),
            max_candidates=4,
            exploration_fraction=0.0,
            max_group_fraction=0.5,
        )
    )

    dominant_count = sum(
        allocation.group_key == "dominant" for allocation in plan.allocations
    )
    assert dominant_count == 2
    assert len(plan.allocations) == 4
