from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from business_master.domain.beliefs import BeliefState, FreshnessPolicy
from business_master.domain.enums import FreshnessMode, HypothesisStatus, HypothesisType
from business_master.domain.hypotheses import EconomicHypothesis, Hypothesis


def test_belief_state_starts_uncertain_without_evidence() -> None:
    belief = BeliefState(hypothesis_id=uuid4())

    assert belief.confidence == 0.0
    assert belief.uncertainty == 1.0
    assert belief.evidence_count == 0
    assert belief.freshness == 1.0
    assert belief.state_version == 1


def test_freshness_policy_requires_parameters_for_decay_modes() -> None:
    with pytest.raises(ValidationError):
        FreshnessPolicy(mode=FreshnessMode.TTL)

    with pytest.raises(ValidationError):
        FreshnessPolicy(mode=FreshnessMode.EXPONENTIAL_DECAY)

    ttl = FreshnessPolicy(mode=FreshnessMode.TTL, ttl_seconds=3600)
    exponential = FreshnessPolicy(
        mode=FreshnessMode.EXPONENTIAL_DECAY,
        half_life_seconds=7200,
    )

    assert ttl.ttl_seconds == 3600
    assert exponential.half_life_seconds == 7200


def test_economic_hypothesis_rejects_self_lineage_and_duplicates() -> None:
    hypothesis_id = uuid4()

    with pytest.raises(ValidationError):
        EconomicHypothesis(
            id=hypothesis_id,
            hypothesis_type=HypothesisType.DEMAND,
            subject="market",
            proposition="Demand exists",
            parent_ids=[hypothesis_id],
        )

    parent_id = uuid4()
    with pytest.raises(ValidationError):
        EconomicHypothesis(
            hypothesis_type=HypothesisType.DEMAND,
            subject="market",
            proposition="Demand exists",
            parent_ids=[parent_id, parent_id],
        )


def test_legacy_conversion_requires_explicit_economic_classification() -> None:
    legacy = Hypothesis(
        name="creator-automation",
        thesis="Creators will buy automated repurposing",
        family="b2b",
        market="US",
        audience="creators",
        active=False,
    )

    converted = EconomicHypothesis.from_legacy(
        legacy,
        hypothesis_type=HypothesisType.OFFER,
        mechanism="Sell a productized repurposing service",
    )

    assert converted.hypothesis_type is HypothesisType.OFFER
    assert converted.subject == legacy.name
    assert converted.proposition == legacy.thesis
    assert converted.legacy_hypothesis_id == legacy.id
    assert converted.context.market == "US"
    assert converted.context.audience == "creators"
    assert converted.context.dimensions["legacy_family"] == "b2b"
    assert converted.status is HypothesisStatus.PAUSED
    assert converted.parent_ids == []
