from uuid import uuid4

from business_master.domain.enums import DecisionType
from business_master.domain.signals import SignalVector
from business_master.policies.feedback import FeedbackPolicy


def test_first_real_external_traction_causes_autonomous_followup() -> None:
    decision = FeedbackPolicy().decide(
        experiment_id=uuid4(),
        signal=SignalVector(
            external_observations=3,
            baseline_sample_size=0,
            attention=None,
        ),
        measurement_window_complete=False,
    )

    assert decision is not None
    assert decision.decision_type == DecisionType.MUTATE


def test_revenue_causes_replication_not_scale() -> None:
    decision = FeedbackPolicy().decide(
        experiment_id=uuid4(),
        signal=SignalVector(revenue=1.0, external_observations=1),
        measurement_window_complete=False,
    )

    assert decision is not None
    assert decision.decision_type == DecisionType.MUTATE


def test_no_signal_after_window_causes_material_mutation() -> None:
    decision = FeedbackPolicy().decide(
        experiment_id=uuid4(),
        signal=SignalVector(
            attention=0.05,
            retention=0.10,
            external_observations=0,
            baseline_sample_size=50,
        ),
        measurement_window_complete=True,
    )

    assert decision is not None
    assert decision.decision_type == DecisionType.MUTATE


def test_incomplete_window_with_no_evidence_waits() -> None:
    decision = FeedbackPolicy().decide(
        experiment_id=uuid4(),
        signal=SignalVector(),
        measurement_window_complete=False,
    )

    assert decision is None
