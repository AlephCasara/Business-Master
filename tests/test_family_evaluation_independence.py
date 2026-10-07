from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from business_master.domain.beliefs import BeliefState
from business_master.domain.enums import (
    ComparisonOperator,
    EvidenceClass,
    EvidenceProvenance,
    EvidenceTier,
    HypothesisType,
    MetricAggregation,
)
from business_master.domain.evidence import EvidenceRecord
from business_master.domain.experiment_contracts import (
    ExperimentContract,
    MeasurementContract,
    MetricCriterion,
)
from business_master.domain.family_evaluation import (
    EvaluationRecommendation,
    FamilyEvaluationContext,
    FamilyEvaluationRequest,
)
from business_master.domain.hypotheses import EconomicHypothesis, EvidenceRequirements
from business_master.policies.family_evaluation import policy_for_family

NOW = datetime(2026, 10, 7, tzinfo=UTC)


def _contract(hypothesis: EconomicHypothesis) -> ExperimentContract:
    return ExperimentContract(
        economic_hypothesis_id=hypothesis.id,
        business_family="b2b",
        question="Do independent companies respond to the same offer?",
        expected_observation="Qualified responses occur across independent companies.",
        falsification_condition="Independent companies reject the offer.",
        measurement=MeasurementContract(
            window_seconds=3600,
            primary_metric="qualified_signal",
            minimum_external_observations=2,
            supporting_criteria=[
                MetricCriterion(
                    metric="qualified_signal",
                    operator=ComparisonOperator.GTE,
                    threshold=2.0,
                    evidence_class=EvidenceClass.MARKET,
                    aggregation=MetricAggregation.SUM,
                    minimum_observations=2,
                )
            ],
        ),
    )


def _reply(
    *,
    source: str,
    company_id: UUID,
    independence_key: str | None = None,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_class=EvidenceClass.MARKET,
        provenance=EvidenceProvenance.OBSERVED_OWN,
        kind="qualified_reply",
        source=source,
        independence_key=independence_key,
        subject_type="company",
        subject_id=company_id,
        observed_at=NOW,
        features={"qualified_signal": 1.0},
    )


def _request(
    hypothesis: EconomicHypothesis,
    evidence: tuple[EvidenceRecord, ...],
) -> FamilyEvaluationRequest:
    return FamilyEvaluationRequest(
        idempotency_key=f"b2b-independence-{hypothesis.id}",
        hypothesis=hypothesis,
        contract=_contract(hypothesis),
        belief_state=BeliefState(hypothesis_id=hypothesis.id, state_version=1),
        evidence=evidence,
        current_tier=EvidenceTier.PROBE,
        context=FamilyEvaluationContext(replication_count=1),
        evaluated_at=NOW,
    )


def _hypothesis() -> EconomicHypothesis:
    return EconomicHypothesis(
        hypothesis_type=HypothesisType.OFFER,
        subject="productized B2B offer",
        proposition="Independent companies respond to the same offer",
        evidence_requirements=EvidenceRequirements(
            minimum_count=2,
            minimum_independent_sources=2,
        ),
    )


def test_b2b_independence_prefers_company_subject_over_transport_source() -> None:
    hypothesis = _hypothesis()
    company_a = uuid4()
    company_b = uuid4()
    evidence = (
        _reply(source="linkedin", company_id=company_a),
        _reply(source="email", company_id=company_a),
        _reply(source="linkedin", company_id=company_b),
    )

    evaluation = policy_for_family("b2b").evaluate(_request(hypothesis, evidence))

    assert evaluation.policy_version == "3"
    assert evaluation.external_observations == 3
    assert evaluation.independent_sources == 2
    assert evaluation.evidence_sufficient is True
    assert evaluation.recommendation is EvaluationRecommendation.GRADUATE


def test_b2b_explicit_independence_key_overrides_subject_identity() -> None:
    hypothesis = _hypothesis()
    duplicated_subject = uuid4()
    evidence = (
        _reply(
            source="crm",
            company_id=duplicated_subject,
            independence_key="company-a",
        ),
        _reply(
            source="crm",
            company_id=duplicated_subject,
            independence_key="company-b",
        ),
    )

    evaluation = policy_for_family("b2b").evaluate(_request(hypothesis, evidence))

    assert evaluation.independent_sources == 2
    assert evaluation.evidence_sufficient is True
    assert evaluation.recommendation is EvaluationRecommendation.GRADUATE


def test_b2b_legacy_evidence_falls_back_to_source_identity() -> None:
    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.OFFER,
        subject="legacy B2B offer",
        proposition="Independent legacy sources respond to the offer",
        evidence_requirements=EvidenceRequirements(
            minimum_count=2,
            minimum_independent_sources=2,
        ),
    )
    evidence = (
        EvidenceRecord(
            evidence_class=EvidenceClass.MARKET,
            provenance=EvidenceProvenance.OBSERVED_OWN,
            kind="qualified_reply",
            source="company-a",
            observed_at=NOW,
            features={"qualified_signal": 1.0},
        ),
        EvidenceRecord(
            evidence_class=EvidenceClass.MARKET,
            provenance=EvidenceProvenance.OBSERVED_OWN,
            kind="qualified_reply",
            source="company-b",
            observed_at=NOW,
            features={"qualified_signal": 1.0},
        ),
    )

    evaluation = policy_for_family("b2b").evaluate(_request(hypothesis, evidence))

    assert evaluation.independent_sources == 2
    assert evaluation.recommendation is EvaluationRecommendation.GRADUATE
