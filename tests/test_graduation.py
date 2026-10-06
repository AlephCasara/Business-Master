from uuid import uuid4

from business_master.domain.enums import DecisionType, EvidenceTier
from business_master.policies.graduation import (
    GraduationEvidence,
    GraduationPolicy,
    next_tier,
)


def test_probe_requires_replication_before_pilot() -> None:
    policy = GraduationPolicy()
    entity_id = uuid4()

    decision = policy.decide(
        entity_id=entity_id,
        current_tier=EvidenceTier.PROBE,
        evidence=GraduationEvidence(
            external_observations=2,
            positive_signals=1,
            replicated_winners=0,
        ),
    )
    assert decision is None

    decision = policy.decide(
        entity_id=entity_id,
        current_tier=EvidenceTier.PROBE,
        evidence=GraduationEvidence(
            external_observations=2,
            positive_signals=1,
            replicated_winners=1,
        ),
    )
    assert decision is not None
    assert decision.decision_type == DecisionType.GRADUATE
    assert next_tier(EvidenceTier.PROBE, decision) == EvidenceTier.PILOT


def test_pilot_requires_multiple_contexts_before_scale() -> None:
    policy = GraduationPolicy()
    entity_id = uuid4()

    insufficient = GraduationEvidence(
        external_observations=6,
        positive_signals=4,
        replicated_winners=3,
        distinct_contexts=1,
    )
    assert (
        policy.decide(
            entity_id=entity_id,
            current_tier=EvidenceTier.PILOT,
            evidence=insufficient,
        )
        is None
    )

    sufficient = GraduationEvidence(
        external_observations=6,
        positive_signals=4,
        replicated_winners=3,
        distinct_contexts=2,
    )
    decision = policy.decide(
        entity_id=entity_id,
        current_tier=EvidenceTier.PILOT,
        evidence=sufficient,
    )
    assert decision is not None
    assert next_tier(EvidenceTier.PILOT, decision) == EvidenceTier.SCALE


def test_technical_failures_do_not_kill_an_economic_hypothesis() -> None:
    policy = GraduationPolicy()
    decision = policy.decide(
        entity_id=uuid4(),
        current_tier=EvidenceTier.PROBE,
        evidence=GraduationEvidence(
            external_observations=0,
            technical_failures=100,
            negative_signals=0,
        ),
    )
    assert decision is None


def test_repeated_external_negative_signal_can_kill() -> None:
    policy = GraduationPolicy(kill_negative_signals=3)
    decision = policy.decide(
        entity_id=uuid4(),
        current_tier=EvidenceTier.PROBE,
        evidence=GraduationEvidence(
            external_observations=3,
            negative_signals=3,
            positive_signals=0,
        ),
    )
    assert decision is not None
    assert decision.decision_type == DecisionType.KILL
