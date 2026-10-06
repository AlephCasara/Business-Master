from uuid import uuid4

from business_master.domain.models import OpportunityScore
from business_master.policies.scoring import ScoringPolicy


def opportunity(**overrides: float) -> OpportunityScore:
    values: dict[str, float | object] = {
        "entity_id": uuid4(),
        "expected_value": 0.0,
        "uncertainty": 0.5,
        "information_gain": 1.0,
        "feedback_speed": 1.0,
        "downstream_reuse": 1.0,
        "compute_cost": 1.0,
        "cash_cost": 0.0,
        "human_time_cost": 0.0,
        "confidence": 0.0,
    }
    values.update(overrides)
    return OpportunityScore.model_validate(values)


def test_bootstrap_prefers_more_information_per_cost() -> None:
    policy = ScoringPolicy()
    cheap_learning = opportunity(information_gain=5.0, compute_cost=1.0)
    expensive_learning = opportunity(information_gain=5.0, compute_cost=10.0)

    assert policy.bootstrap_priority(cheap_learning) > policy.bootstrap_priority(expensive_learning)


def test_mature_policy_weights_real_expected_value_more() -> None:
    policy = ScoringPolicy()
    profitable = opportunity(expected_value=10.0, information_gain=0.1)
    educational = opportunity(expected_value=0.0, information_gain=2.0)

    assert policy.mature_priority(profitable) > policy.mature_priority(educational)
