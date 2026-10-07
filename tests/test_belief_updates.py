from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from business_master.domain.belief_updates import (
    BeliefUpdateRequest,
    BoundedLinearBeliefUpdatePolicy,
    EvidenceInterpretation,
    freshness_weight,
)
from business_master.domain.beliefs import BeliefState, FreshnessPolicy
from business_master.domain.enums import (
    EvidenceClass,
    EvidenceProvenance,
    FreshnessMode,
    HypothesisType,
)
from business_master.domain.evidence import EvidenceRecord
from business_master.domain.hypotheses import EconomicHypothesis


def _hypothesis(freshness_policy: FreshnessPolicy | None = None) -> EconomicHypothesis:
    return EconomicHypothesis(
        hypothesis_type=HypothesisType.DEMAND,
        subject="qualified demand",
        proposition="Qualified prospects will respond to the offer",
        freshness_policy=freshness_policy or FreshnessPolicy(),
    )


def _evidence(
    hypothesis: EconomicHypothesis,
    *,
    evidence_class: EvidenceClass = EvidenceClass.MARKET,
    observed_at: datetime,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_class=evidence_class,
        provenance=EvidenceProvenance.OBSERVED_OWN,
        kind="qualified_reply",
        source="test",
        subject_type="economic_hypothesis",
        subject_id=hypothesis.id,
        observed_at=observed_at,
    )


def test_freshness_modes_are_deterministic() -> None:
    observed_at = datetime(2026, 1, 1, tzinfo=UTC)
    as_of = observed_at + timedelta(seconds=50)

    assert freshness_weight(FreshnessPolicy(), observed_at, as_of) == 1.0
    assert freshness_weight(
        FreshnessPolicy(mode=FreshnessMode.TTL, ttl_seconds=100),
        observed_at,
        as_of,
    ) == 1.0
    assert freshness_weight(
        FreshnessPolicy(mode=FreshnessMode.LINEAR_DECAY, ttl_seconds=100),
        observed_at,
        as_of,
    ) == pytest.approx(0.5)
    assert freshness_weight(
        FreshnessPolicy(mode=FreshnessMode.EXPONENTIAL_DECAY, half_life_seconds=50),
        observed_at,
        as_of,
    ) == pytest.approx(0.5)


def test_supporting_and_falsifying_updates_are_bounded_and_versioned() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    hypothesis = _hypothesis()
    supporting = _evidence(hypothesis, observed_at=now)
    current = BeliefState(
        hypothesis_id=hypothesis.id,
        confidence=0.2,
        uncertainty=0.8,
        evidence_count=2,
        state_version=4,
    )
    policy = BoundedLinearBeliefUpdatePolicy()

    support_result = policy.apply(
        hypothesis=hypothesis,
        evidence=supporting,
        current=current,
        request=BeliefUpdateRequest(
            hypothesis_id=hypothesis.id,
            evidence_id=supporting.id,
            interpretation=EvidenceInterpretation.SUPPORTING,
            rationale="Observed qualified response supports demand",
            evaluated_at=now,
        ),
    )

    assert support_result.update.applied is True
    assert support_result.state.confidence == pytest.approx(0.6)
    assert support_result.state.uncertainty == pytest.approx(0.4)
    assert support_result.state.evidence_count == 3
    assert support_result.state.state_version == 5

    falsifying = _evidence(hypothesis, observed_at=now + timedelta(seconds=1))
    falsify_result = policy.apply(
        hypothesis=hypothesis,
        evidence=falsifying,
        current=support_result.state,
        request=BeliefUpdateRequest(
            hypothesis_id=hypothesis.id,
            evidence_id=falsifying.id,
            interpretation=EvidenceInterpretation.FALSIFYING,
            rationale="Qualified exposure produced a falsifying observation",
            evaluated_at=now + timedelta(seconds=1),
        ),
    )

    assert falsify_result.state.confidence == pytest.approx(0.3)
    assert falsify_result.state.uncertainty == pytest.approx(0.2)
    assert falsify_result.state.evidence_count == 4
    assert falsify_result.state.state_version == 6


def test_stale_evidence_is_audited_without_changing_state() -> None:
    observed_at = datetime(2026, 1, 1, tzinfo=UTC)
    evaluated_at = observed_at + timedelta(seconds=101)
    hypothesis = _hypothesis(FreshnessPolicy(mode=FreshnessMode.TTL, ttl_seconds=100))
    evidence = _evidence(hypothesis, observed_at=observed_at)
    current = BeliefState(hypothesis_id=hypothesis.id, confidence=0.4, uncertainty=0.6)

    result = BoundedLinearBeliefUpdatePolicy().apply(
        hypothesis=hypothesis,
        evidence=evidence,
        current=current,
        request=BeliefUpdateRequest(
            hypothesis_id=hypothesis.id,
            evidence_id=evidence.id,
            interpretation=EvidenceInterpretation.SUPPORTING,
            rationale="Old observation",
            evaluated_at=evaluated_at,
        ),
    )

    assert result.update.applied is False
    assert result.update.freshness_weight == 0.0
    assert result.update.effective_weight == 0.0
    assert result.update.resulting_state_version == current.state_version
    assert result.state == current


def test_technical_failure_cannot_falsify_market_hypothesis() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    hypothesis = _hypothesis()
    evidence = _evidence(
        hypothesis,
        evidence_class=EvidenceClass.TECHNICAL,
        observed_at=now,
    )
    current = BeliefState(hypothesis_id=hypothesis.id, confidence=0.7, uncertainty=0.3)
    policy = BoundedLinearBeliefUpdatePolicy()

    with pytest.raises(ValueError, match="technical evidence cannot support or falsify"):
        policy.apply(
            hypothesis=hypothesis,
            evidence=evidence,
            current=current,
            request=BeliefUpdateRequest(
                hypothesis_id=hypothesis.id,
                evidence_id=evidence.id,
                interpretation=EvidenceInterpretation.FALSIFYING,
                rationale="Renderer failed",
                evaluated_at=now,
            ),
        )

    result = policy.apply(
        hypothesis=hypothesis,
        evidence=evidence,
        current=current,
        request=BeliefUpdateRequest(
            hypothesis_id=hypothesis.id,
            evidence_id=evidence.id,
            interpretation=EvidenceInterpretation.TECHNICAL,
            rationale="Renderer failed",
            evaluated_at=now,
        ),
    )

    assert result.update.applied is False
    assert result.state == current
    assert result.update.policy_rationale.startswith("technical evidence")


def test_request_requires_matching_ids_and_aware_time() -> None:
    hypothesis = _hypothesis()
    now = datetime(2026, 1, 1, tzinfo=UTC)
    evidence = _evidence(hypothesis, observed_at=now)
    current = BeliefState(hypothesis_id=hypothesis.id)

    with pytest.raises(ValueError, match="evidence IDs do not match"):
        BoundedLinearBeliefUpdatePolicy().apply(
            hypothesis=hypothesis,
            evidence=evidence,
            current=current,
            request=BeliefUpdateRequest(
                hypothesis_id=hypothesis.id,
                evidence_id=uuid4(),
                interpretation=EvidenceInterpretation.SUPPORTING,
                rationale="Wrong evidence ID",
                evaluated_at=now,
            ),
        )

    with pytest.raises(ValueError, match="timezone-aware"):
        BeliefUpdateRequest(
            hypothesis_id=hypothesis.id,
            evidence_id=evidence.id,
            interpretation=EvidenceInterpretation.SUPPORTING,
            rationale="Naive clock",
            evaluated_at=datetime(2026, 1, 1),
        )
