from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import BaseModel, Field, model_validator

from business_master.domain.belief_updates import EvidenceInterpretation
from business_master.domain.beliefs import BeliefState
from business_master.domain.clock import utcnow
from business_master.domain.enums import EvidenceTier
from business_master.domain.evidence import EvidenceRecord
from business_master.domain.experiment_contracts import ExperimentContract
from business_master.domain.hypotheses import EconomicHypothesis
from business_master.domain.ledger import EconomicLedgerSnapshot


class BusinessFamily(StrEnum):
    CONTENT = "content"
    B2B = "b2b"
    COMMERCE = "commerce"
    CAPABILITY = "capability"


class ReadinessStatus(StrEnum):
    UNKNOWN = "unknown"
    NOT_READY = "not_ready"
    READY = "ready"


class EvaluationRecommendation(StrEnum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    CONTINUE = "continue"
    REPLICATE = "replicate"
    GRADUATE = "graduate"
    PAUSE = "pause"
    REJECT = "reject"


class CriterionRole(StrEnum):
    SUPPORTING = "supporting"
    FALSIFYING = "falsifying"


class CriterionEvaluation(BaseModel):
    role: CriterionRole
    metric: str
    evidence_class: str
    aggregation: str
    operator: str
    threshold: float
    observation_count: int = Field(ge=0)
    aggregated_value: float | None = None
    met: bool
    evidence_ids: list[UUID] = Field(default_factory=list)


class EvidenceInterpretationDecision(BaseModel):
    evidence_id: UUID
    interpretation: EvidenceInterpretation
    strength: float = Field(gt=0.0, le=1.0)
    rationale: str = Field(min_length=1, max_length=1000)


class FamilyEvaluationContext(BaseModel):
    """Explicit structural facts not inferable from one evidence record.

    These values are expected to come from experiment lineage/runtime state. PR8 does
    not invent replications or contexts from filenames, sources, or generated prose.
    """

    replication_count: int = Field(default=0, ge=0)
    distinct_contexts: int = Field(default=0, ge=0)
    operational_successes: int = Field(default=0, ge=0)
    operational_failures: int = Field(default=0, ge=0)
    severe_risk_events: int = Field(default=0, ge=0)


class FamilyEvaluationRequest(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=255)
    hypothesis: EconomicHypothesis
    contract: ExperimentContract
    belief_state: BeliefState
    evidence: tuple[EvidenceRecord, ...]
    current_tier: EvidenceTier = EvidenceTier.PROBE
    context: FamilyEvaluationContext = Field(default_factory=FamilyEvaluationContext)
    economic_snapshot: EconomicLedgerSnapshot | None = None
    evaluated_at: datetime = Field(default_factory=utcnow)

    @model_validator(mode="after")
    def validate_alignment(self) -> FamilyEvaluationRequest:
        if self.contract.economic_hypothesis_id != self.hypothesis.id:
            raise ValueError("experiment contract does not belong to the economic hypothesis")
        if self.belief_state.hypothesis_id != self.hypothesis.id:
            raise ValueError("belief state does not belong to the economic hypothesis")
        if self.evaluated_at.tzinfo is None or self.evaluated_at.utcoffset() is None:
            raise ValueError("evaluated_at must be timezone-aware")
        if self.idempotency_key != self.idempotency_key.strip():
            raise ValueError("idempotency_key must be trimmed")
        evidence_ids = [record.id for record in self.evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("evaluation evidence cannot contain duplicate records")
        return self


class FamilyEvaluation(BaseModel):
    id: UUID
    idempotency_key: str
    family: BusinessFamily
    hypothesis_id: UUID
    contract_id: UUID
    belief_state_version: int = Field(ge=1)
    current_tier: EvidenceTier
    policy_name: str
    policy_version: str
    evidence_ids: list[UUID]
    interpretations: list[EvidenceInterpretationDecision]
    criteria: list[CriterionEvaluation]
    external_observations: int = Field(ge=0)
    independent_sources: int = Field(ge=0)
    replication_count: int = Field(ge=0)
    distinct_contexts: int = Field(ge=0)
    evidence_sufficient: bool
    supporting_signal: bool
    falsified: bool
    economic_readiness: ReadinessStatus
    operational_readiness: ReadinessStatus
    recommendation: EvaluationRecommendation
    rationale: str
    evaluated_at: datetime

    @classmethod
    def deterministic_id(cls, idempotency_key: str) -> UUID:
        return uuid5(NAMESPACE_URL, f"business-master/family-evaluation/{idempotency_key}")
