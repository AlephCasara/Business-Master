from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from business_master.domain.beliefs import BeliefState
from business_master.domain.enums import (
    ComparisonOperator,
    EvidenceClass,
    EvidenceProvenance,
    EvidenceTier,
    HypothesisType,
    MetricAggregation,
)
from business_master.domain.evidence import EvidenceRecord, EvidenceScalar
from business_master.domain.experiment_contracts import (
    ExperimentContract,
    MeasurementContract,
    MetricCriterion,
)
from business_master.domain.family_evaluation import (
    EvaluationRecommendation,
    FamilyEvaluationContext,
    FamilyEvaluationRequest,
    ReadinessStatus,
)
from business_master.domain.hypotheses import (
    EconomicHypothesis,
    EvidenceRequirements,
)
from business_master.domain.ledger import EconomicLedgerSnapshot
from business_master.policies.family_evaluation import policy_for_family

NOW = datetime(2026, 10, 7, tzinfo=UTC)


def _contract(hypothesis: EconomicHypothesis, family: str) -> ExperimentContract:
    return ExperimentContract(
        economic_hypothesis_id=hypothesis.id,
        business_family=family,
        question="Does the bounded experiment produce the target signal?",
        expected_observation="The target metric clears the supporting threshold.",
        falsification_condition="The failure metric clears the falsifying threshold.",
        measurement=MeasurementContract(
            window_seconds=3600,
            primary_metric="qualified_signal",
            minimum_external_observations=1,
            supporting_criteria=[
                MetricCriterion(
                    metric="qualified_signal",
                    operator=ComparisonOperator.GTE,
                    threshold=1.0,
                    evidence_class=EvidenceClass.MARKET,
                    aggregation=MetricAggregation.SUM,
                    minimum_observations=1,
                )
            ],
            falsifying_criteria=[
                MetricCriterion(
                    metric="rejection",
                    operator=ComparisonOperator.GTE,
                    threshold=1.0,
                    evidence_class=EvidenceClass.MARKET,
                    aggregation=MetricAggregation.SUM,
                    minimum_observations=1,
                )
            ],
        ),
    )


def _evidence(
    *,
    source: str,
    kind: str,
    evidence_class: EvidenceClass = EvidenceClass.MARKET,
    qualified_signal: float | None = None,
    rejection: float | None = None,
) -> EvidenceRecord:
    features: dict[str, EvidenceScalar] = {}
    if qualified_signal is not None:
        features["qualified_signal"] = qualified_signal
    if rejection is not None:
        features["rejection"] = rejection
    return EvidenceRecord(
        evidence_class=evidence_class,
        provenance=EvidenceProvenance.OBSERVED_OWN,
        kind=kind,
        source=source,
        observed_at=NOW,
        features=features,
    )


def _request(
    *,
    family: str,
    hypothesis: EconomicHypothesis,
    evidence: tuple[EvidenceRecord, ...],
    tier: EvidenceTier = EvidenceTier.PROBE,
    context: FamilyEvaluationContext | None = None,
    snapshot: EconomicLedgerSnapshot | None = None,
) -> FamilyEvaluationRequest:
    return FamilyEvaluationRequest(
        idempotency_key=f"{family}-{tier.value}-{hypothesis.id}",
        hypothesis=hypothesis,
        contract=_contract(hypothesis, family),
        belief_state=BeliefState(hypothesis_id=hypothesis.id, state_version=3),
        evidence=evidence,
        current_tier=tier,
        context=context or FamilyEvaluationContext(),
        economic_snapshot=snapshot,
        evaluated_at=NOW,
    )


def test_content_policy_uses_contract_criteria_and_replication_gate() -> None:
    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.HOOK,
        subject="content hook",
        proposition="The hook produces qualified external intent",
    )
    signal = _evidence(source="youtube", kind="click", qualified_signal=1.0)

    without_replication = policy_for_family("content").evaluate(
        _request(family="content", hypothesis=hypothesis, evidence=(signal,))
    )
    assert without_replication.supporting_signal is True
    assert without_replication.evidence_sufficient is True
    assert without_replication.recommendation is EvaluationRecommendation.REPLICATE
    assert without_replication.interpretations[0].interpretation.value == "supporting"

    with_replication = policy_for_family("content").evaluate(
        _request(
            family="content",
            hypothesis=hypothesis,
            evidence=(signal,),
            context=FamilyEvaluationContext(replication_count=1),
        )
    )
    assert with_replication.recommendation is EvaluationRecommendation.GRADUATE


def test_b2b_policy_requires_independent_companies_and_scale_economics() -> None:
    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.OFFER,
        subject="productized B2B offer",
        proposition="Independent qualified companies buy the same bounded offer",
        evidence_requirements=EvidenceRequirements(
            minimum_count=2,
            minimum_independent_sources=2,
        ),
    )
    evidence = (
        _evidence(source="company-a", kind="qualified_reply", qualified_signal=1.0),
        _evidence(source="company-b", kind="qualified_reply", qualified_signal=1.0),
    )

    probe = policy_for_family("b2b").evaluate(
        _request(
            family="b2b",
            hypothesis=hypothesis,
            evidence=evidence,
            context=FamilyEvaluationContext(replication_count=1),
        )
    )
    assert probe.independent_sources == 2
    assert probe.recommendation is EvaluationRecommendation.GRADUATE

    unprofitable = EconomicLedgerSnapshot(
        currency="USD",
        recognized_revenue=Decimal("100"),
        acquisition_spend=Decimal("120"),
        contribution_after_acquisition=Decimal("-20"),
    )
    pilot = policy_for_family("b2b").evaluate(
        _request(
            family="b2b",
            hypothesis=hypothesis,
            evidence=evidence,
            tier=EvidenceTier.PILOT,
            context=FamilyEvaluationContext(
                replication_count=2,
                distinct_contexts=2,
                operational_successes=2,
            ),
            snapshot=unprofitable,
        )
    )
    assert pilot.economic_readiness is ReadinessStatus.NOT_READY
    assert pilot.recommendation is EvaluationRecommendation.REPLICATE

    profitable = unprofitable.model_copy(
        update={"contribution_after_acquisition": Decimal("30")}
    )
    scale_ready = policy_for_family("b2b").evaluate(
        _request(
            family="b2b",
            hypothesis=hypothesis,
            evidence=evidence,
            tier=EvidenceTier.PILOT,
            context=FamilyEvaluationContext(
                replication_count=2,
                distinct_contexts=2,
                operational_successes=2,
            ),
            snapshot=profitable,
        )
    )
    assert scale_ready.economic_readiness is ReadinessStatus.READY
    assert scale_ready.operational_readiness is ReadinessStatus.READY
    assert scale_ready.recommendation is EvaluationRecommendation.GRADUATE


def test_commerce_falsification_rejects_only_after_sufficient_evidence() -> None:
    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.PRODUCT,
        subject="commerce offer",
        proposition="The product receives qualified demand",
        evidence_requirements=EvidenceRequirements(minimum_count=2),
    )
    rejection = _evidence(source="shop", kind="rejection", rejection=1.0)

    early = policy_for_family("commerce").evaluate(
        _request(family="commerce", hypothesis=hypothesis, evidence=(rejection,))
    )
    assert early.falsified is True
    assert early.evidence_sufficient is False
    assert early.recommendation is EvaluationRecommendation.INSUFFICIENT_EVIDENCE

    second = _evidence(source="shop-2", kind="rejection", rejection=1.0)
    sufficient = policy_for_family("commerce").evaluate(
        _request(family="commerce", hypothesis=hypothesis, evidence=(rejection, second))
    )
    assert sufficient.evidence_sufficient is True
    assert sufficient.recommendation is EvaluationRecommendation.REJECT


def test_capability_policy_keeps_technical_failure_out_of_economic_interpretation() -> None:
    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.CAPABILITY,
        subject="local renderer",
        proposition="The local renderer can execute the workload reliably",
    )
    technical = _evidence(
        source="worker",
        kind="renderer_crash",
        evidence_class=EvidenceClass.TECHNICAL,
    )
    market_signal = _evidence(
        source="benchmark",
        kind="quality_pass",
        qualified_signal=1.0,
    )

    evaluation = policy_for_family("capability").evaluate(
        _request(
            family="capability",
            hypothesis=hypothesis,
            evidence=(technical, market_signal),
            context=FamilyEvaluationContext(
                replication_count=1,
                operational_failures=1,
            ),
        )
    )

    technical_interpretation = next(
        item for item in evaluation.interpretations if item.evidence_id == technical.id
    )
    assert technical_interpretation.interpretation.value == "technical"
    assert evaluation.operational_readiness is ReadinessStatus.NOT_READY
    assert evaluation.recommendation is EvaluationRecommendation.REPLICATE


def test_unknown_family_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported business family"):
        policy_for_family("unknown-family")
