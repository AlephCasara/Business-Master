from uuid import uuid4

import pytest

from business_master.controllers.experiments import ExperimentController
from business_master.controllers.reconciler import (
    ReconcileActionType,
    ReconcilePolicy,
    ReconcileSnapshot,
)
from business_master.domain.enums import DecisionType, EvidenceTier
from business_master.domain.models import Hypothesis, OpportunityScore
from business_master.domain.signals import SignalVector
from business_master.policies.allocation import AllocationCandidate, AllocationPolicy
from business_master.policies.feedback import FeedbackPolicy
from business_master.policies.graduation import (
    GraduationEvidence,
    GraduationPolicy,
    next_tier,
)
from business_master.policies.scoring import ScoringPolicy


def _opportunity(**overrides: float) -> OpportunityScore:
    values: dict[str, float | object] = {
        "entity_id": uuid4(),
        "expected_value": 10.0,
        "uncertainty": 0.2,
        "information_gain": 2.0,
        "feedback_speed": 0.5,
        "downstream_reuse": 3.0,
        "compute_cost": 1.0,
        "cash_cost": 2.0,
        "human_time_cost": 1.0,
        "confidence": 0.4,
    }
    values.update(overrides)
    return OpportunityScore.model_validate(values)


def test_pr0_bootstrap_scoring_numeric_contract() -> None:
    """Freeze the V0 scalar-cost bootstrap heuristic until its adapter is retired."""
    score = ScoringPolicy().bootstrap_priority(_opportunity())

    assert score == pytest.approx(2.269999812500047, rel=1e-12)


def test_pr0_mature_scoring_numeric_contract() -> None:
    """Freeze the V0 mature expected-value weighting during structural refactors."""
    score = ScoringPolicy().mature_priority(_opportunity())

    assert score == pytest.approx(7.234999943750014, rel=1e-12)


def test_pr0_allocator_numeric_contract() -> None:
    """Characterize the legacy fungible-unit exploration/exploitation allocator."""
    probe = uuid4()
    scale = uuid4()

    allocations = AllocationPolicy(
        exploration_fraction=0.20,
        max_candidate_fraction=0.80,
    ).allocate(
        [
            AllocationCandidate(probe, EvidenceTier.PROBE, priority=0.1),
            AllocationCandidate(scale, EvidenceTier.SCALE, priority=10.0),
        ],
        total_units=100.0,
    )
    by_id = {allocation.entity_id: allocation.units for allocation in allocations}

    assert by_id == pytest.approx({probe: 20.0, scale: 80.0})


def test_pr0_feedback_revenue_creates_followup_not_scale() -> None:
    """Early revenue is evidence for a follow-up experiment, not direct graduation."""
    decision = FeedbackPolicy().decide(
        experiment_id=uuid4(),
        signal=SignalVector(revenue=1.0, external_observations=1),
        measurement_window_complete=False,
    )

    assert decision is not None
    assert decision.decision_type == DecisionType.MUTATE


def test_pr0_incomplete_measurement_without_evidence_waits() -> None:
    decision = FeedbackPolicy().decide(
        experiment_id=uuid4(),
        signal=SignalVector(),
        measurement_window_complete=False,
    )

    assert decision is None


def test_pr0_probe_graduation_requires_replication_contract() -> None:
    policy = GraduationPolicy()
    entity_id = uuid4()

    without_replication = policy.decide(
        entity_id=entity_id,
        current_tier=EvidenceTier.PROBE,
        evidence=GraduationEvidence(
            external_observations=2,
            positive_signals=1,
            replicated_winners=0,
        ),
    )
    assert without_replication is None

    with_replication = policy.decide(
        entity_id=entity_id,
        current_tier=EvidenceTier.PROBE,
        evidence=GraduationEvidence(
            external_observations=2,
            positive_signals=1,
            replicated_winners=1,
        ),
    )
    assert with_replication is not None
    assert with_replication.decision_type == DecisionType.GRADUATE
    assert next_tier(EvidenceTier.PROBE, with_replication) == EvidenceTier.PILOT


def test_pr0_technical_failure_is_not_market_rejection_contract() -> None:
    decision = GraduationPolicy().decide(
        entity_id=uuid4(),
        current_tier=EvidenceTier.PROBE,
        evidence=GraduationEvidence(
            technical_failures=100,
            external_observations=0,
            negative_signals=0,
        ),
    )

    assert decision is None


def test_pr0_mutation_lineage_contract() -> None:
    controller = ExperimentController()
    hypothesis = Hypothesis(
        name="baseline-content",
        thesis="A bounded content probe can produce external evidence",
        family="content",
    )
    parent = controller.create_probe(
        hypothesis,
        dimensions={"hook": "A", "topic": "X", "visual": "bar"},
    )

    child = controller.mutate(
        parent,
        changed_dimensions={"hook": "B"},
        preserve_dimensions=("topic", "visual"),
        rationale="Characterization test for PR0 lineage semantics.",
    )

    assert child.parent_id == parent.id
    assert child.tier == EvidenceTier.PROBE
    assert child.dimensions == {"hook": "B", "topic": "X", "visual": "bar"}
    assert child.mutation is not None
    assert child.mutation.parent_experiment_id == parent.id
    assert child.mutation.changed_dimensions == {"hook": "B"}
    assert child.mutation.preserved_dimensions == ["topic", "visual"]


def test_pr0_reconciler_prioritizes_measurement_before_new_work_contract() -> None:
    due = uuid4()
    ready = uuid4()
    runnable = uuid4()
    probe = uuid4()

    actions = ReconcilePolicy().plan(
        ReconcileSnapshot(
            hypotheses_without_live_experiment=(probe,),
            runnable_experiments=(runnable,),
            experiments_due_for_measurement=(due,),
            experiments_ready_for_evaluation=(ready,),
            available_execution_slots=1,
            available_probe_slots=1,
        )
    )

    assert [action.kind for action in actions[:2]] == [
        ReconcileActionType.REQUEST_MEASUREMENT,
        ReconcileActionType.EVALUATE_EXPERIMENT,
    ]


def test_pr0_hypothesis_can_spawn_probe_without_human_instruction_contract() -> None:
    hypothesis_id = uuid4()
    actions = ReconcilePolicy().plan(
        ReconcileSnapshot(
            hypotheses_without_live_experiment=(hypothesis_id,),
            available_probe_slots=1,
        )
    )

    assert len(actions) == 1
    assert actions[0].kind == ReconcileActionType.CREATE_PROBE
    assert actions[0].entity_id == hypothesis_id
