"""Backward-compatible facade for V0 domain model imports.

PR1 decomposes the former monolithic models module into cohesive domain modules.
Existing callers may continue importing from ``business_master.domain.models``
while newer code imports from the owning module directly.
"""

from business_master.domain.clock import utcnow
from business_master.domain.decisions import Decision
from business_master.domain.economics import BusinessOutcome, OpportunityScore
from business_master.domain.evidence import EvidenceRef
from business_master.domain.execution import ExecutionResult
from business_master.domain.experiments import Experiment, MetricSnapshot, MutationSpec
from business_master.domain.human import HumanActionRequest
from business_master.domain.hypotheses import Hypothesis
from business_master.domain.resources import Resource

__all__ = [
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
]
