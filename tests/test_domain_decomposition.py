from business_master.domain import models as legacy_models
from business_master.domain.clock import utcnow
from business_master.domain.decisions import Decision
from business_master.domain.economics import BusinessOutcome, OpportunityScore
from business_master.domain.evidence import EvidenceRef
from business_master.domain.execution import ExecutionResult
from business_master.domain.experiments import Experiment, MetricSnapshot, MutationSpec
from business_master.domain.human import HumanActionRequest
from business_master.domain.hypotheses import Hypothesis
from business_master.domain.resources import Resource


def test_legacy_models_facade_reexports_exact_domain_classes() -> None:
    assert legacy_models.EvidenceRef is EvidenceRef
    assert legacy_models.Hypothesis is Hypothesis
    assert legacy_models.MutationSpec is MutationSpec
    assert legacy_models.Experiment is Experiment
    assert legacy_models.MetricSnapshot is MetricSnapshot
    assert legacy_models.BusinessOutcome is BusinessOutcome
    assert legacy_models.OpportunityScore is OpportunityScore
    assert legacy_models.Decision is Decision
    assert legacy_models.Resource is Resource
    assert legacy_models.ExecutionResult is ExecutionResult
    assert legacy_models.HumanActionRequest is HumanActionRequest
    assert legacy_models.utcnow is utcnow


def test_legacy_facade_exports_the_v0_public_surface() -> None:
    assert set(legacy_models.__all__) == {
        "BusinessOutcome",
        "Decision",
        "EvidenceRef",
        "ExecutionResult",
        "Experiment",
        "HumanActionRequest",
        "Hypothesis",
        "MetricSnapshot",
        "MutationSpec",
        "OpportunityScore",
        "Resource",
        "utcnow",
    }


def test_hypothesis_defaults_are_preserved_after_module_move() -> None:
    hypothesis = Hypothesis(name="test", thesis="test thesis", family="content")

    assert hypothesis.market is None
    assert hypothesis.audience is None
    assert hypothesis.parent_id is None
    assert hypothesis.evidence_ids == []
    assert hypothesis.active is True
    assert hypothesis.created_at.tzinfo is not None
    assert hypothesis.updated_at.tzinfo is not None
