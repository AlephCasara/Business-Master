from business_master.controllers.experiments import ExperimentController
from business_master.domain.enums import EvidenceTier
from business_master.domain.models import Hypothesis


def test_probe_is_zero_cash_by_default() -> None:
    hypothesis = Hypothesis(name="charts", thesis="Charts can earn external attention", family="content")
    experiment = ExperimentController().create_probe(
        hypothesis,
        dimensions={"hook": "baseline", "topic": "market"},
        expected_compute_units=1.0,
    )

    assert experiment.expected_cash_cost == 0.0
    assert experiment.tier == EvidenceTier.PROBE
    assert experiment.parent_id is None


def test_mutation_preserves_lineage_and_does_not_auto_graduate() -> None:
    controller = ExperimentController()
    hypothesis = Hypothesis(name="charts", thesis="Charts can earn external attention", family="content")
    parent = controller.create_probe(
        hypothesis,
        dimensions={"hook": "A", "topic": "X", "visual": "bar"},
    )

    child = controller.mutate(
        parent,
        changed_dimensions={"hook": "B"},
        preserve_dimensions=("topic", "visual"),
        rationale="External evidence justified hook replication.",
    )

    assert child.parent_id == parent.id
    assert child.tier == parent.tier == EvidenceTier.PROBE
    assert child.dimensions == {"hook": "B", "topic": "X", "visual": "bar"}
    assert child.mutation is not None
    assert child.mutation.parent_experiment_id == parent.id


def test_mutation_rejects_fake_change() -> None:
    controller = ExperimentController()
    hypothesis = Hypothesis(name="h", thesis="t", family="content")
    parent = controller.create_probe(hypothesis)

    try:
        controller.mutate(parent, changed_dimensions={}, rationale="none")
    except ValueError as exc:
        assert "at least one" in str(exc)
    else:
        raise AssertionError("empty mutation should fail")
