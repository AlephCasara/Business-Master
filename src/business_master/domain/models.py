"""Backward-compatible facade for domain model imports.

PR1 decomposed the former monolithic models module into cohesive domain modules.
PR2 adds V2 economic hypotheses and beliefs without removing the V0 models.
Existing callers may continue importing from ``business_master.domain.models``
while newer code imports from the owning module directly.
"""

from business_master.domain.beliefs import BeliefState, FreshnessPolicy
from business_master.domain.clock import utcnow
from business_master.domain.decisions import Decision
from business_master.domain.economics import BusinessOutcome, OpportunityScore
from business_master.domain.evidence import EvidenceRef
from business_master.domain.execution import ExecutionResult
from business_master.domain.experiments import Experiment, MetricSnapshot, MutationSpec
from business_master.domain.human import HumanActionRequest
from business_master.domain.hypotheses import (
    BeliefContext,
    EconomicHypothesis,
    EvidenceRequirements,
    Hypothesis,
)
from business_master.domain.resources import Resource

__all__ = [
    "BeliefContext",
    "BeliefState",
    "BusinessOutcome",
    "Decision",
    "EconomicHypothesis",
    "EvidenceRef",
    "EvidenceRequirements",
    "ExecutionResult",
    "Experiment",
    "FreshnessPolicy",
    "HumanActionRequest",
    "Hypothesis",
    "MetricSnapshot",
    "MutationSpec",
    "OpportunityScore",
    "Resource",
    "utcnow",
]
