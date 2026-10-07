from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from math import pow
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from business_master.domain.beliefs import BeliefState, FreshnessPolicy
from business_master.domain.clock import utcnow
from business_master.domain.enums import EvidenceClass, FreshnessMode
from business_master.domain.evidence import EvidenceRecord
from business_master.domain.hypotheses import EconomicHypothesis


class EvidenceInterpretation(StrEnum):
    SUPPORTING = "supporting"
    FALSIFYING = "falsifying"
    NEUTRAL = "neutral"
    TECHNICAL = "technical"


class BeliefUpdateRequest(BaseModel):
    hypothesis_id: UUID
    evidence_id: UUID
    interpretation: EvidenceInterpretation
    strength: float = Field(default=1.0, gt=0.0, le=1.0)
    rationale: str = Field(min_length=1, max_length=1000)
    evaluated_at: datetime = Field(default_factory=utcnow)

    @field_validator("rationale")
    @classmethod
    def validate_rationale(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("rationale must be trimmed")
        return value

    @field_validator("evaluated_at")
    @classmethod
    def validate_evaluated_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("evaluated_at must be timezone-aware")
        return value


class BeliefUpdateRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    hypothesis_id: UUID
    evidence_id: UUID
    interpretation: EvidenceInterpretation
    strength: float = Field(gt=0.0, le=1.0)
    interpretation_rationale: str
    policy_name: str
    policy_version: str
    evidence_class: EvidenceClass
    freshness_weight: float = Field(ge=0.0, le=1.0)
    effective_weight: float = Field(ge=0.0, le=1.0)
    prior_state_version: int = Field(ge=1)
    resulting_state_version: int = Field(ge=1)
    confidence_before: float = Field(ge=0.0, le=1.0)
    confidence_after: float = Field(ge=0.0, le=1.0)
    uncertainty_before: float = Field(ge=0.0, le=1.0)
    uncertainty_after: float = Field(ge=0.0, le=1.0)
    evidence_count_before: int = Field(ge=0)
    evidence_count_after: int = Field(ge=0)
    applied: bool
    policy_rationale: str
    evaluated_at: datetime
    created_at: datetime = Field(default_factory=utcnow)


class BeliefUpdateResult(BaseModel):
    state: BeliefState
    update: BeliefUpdateRecord


def freshness_weight(
    policy: FreshnessPolicy,
    observed_at: datetime,
    as_of: datetime,
) -> float:
    if observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ValueError("evidence observed_at must be timezone-aware")
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("freshness evaluation time must be timezone-aware")

    age_seconds = max(0.0, (as_of - observed_at).total_seconds())

    if policy.mode is FreshnessMode.NONE:
        return 1.0
    if policy.mode is FreshnessMode.TTL:
        assert policy.ttl_seconds is not None
        return 1.0 if age_seconds <= policy.ttl_seconds else 0.0
    if policy.mode is FreshnessMode.LINEAR_DECAY:
        assert policy.ttl_seconds is not None
        return max(0.0, 1.0 - (age_seconds / policy.ttl_seconds))
    if policy.mode is FreshnessMode.EXPONENTIAL_DECAY:
        assert policy.half_life_seconds is not None
        return pow(0.5, age_seconds / policy.half_life_seconds)
    raise ValueError(f"unsupported freshness mode: {policy.mode}")


class BoundedLinearBeliefUpdatePolicy:
    """Small deterministic bootstrap policy for evidence -> belief transitions.

    The policy deliberately does not infer whether evidence supports or falsifies a
    hypothesis. That interpretation is an explicit input and is persisted. Later
    business-family policies can decide how evidence is interpreted without changing
    this substrate's versioning, freshness, idempotency, or lineage semantics.
    """

    name = "bounded_linear_belief_update"
    version = "1"
    learning_rate = 0.5

    def apply(
        self,
        *,
        hypothesis: EconomicHypothesis,
        evidence: EvidenceRecord,
        current: BeliefState,
        request: BeliefUpdateRequest,
    ) -> BeliefUpdateResult:
        if request.hypothesis_id != hypothesis.id or current.hypothesis_id != hypothesis.id:
            raise ValueError("belief update hypothesis IDs do not match")
        if request.evidence_id != evidence.id:
            raise ValueError("belief update evidence IDs do not match")

        self._validate_interpretation(evidence, request.interpretation)
        freshness = freshness_weight(
            hypothesis.freshness_policy,
            evidence.observed_at,
            request.evaluated_at,
        )

        applied = (
            request.interpretation
            in {EvidenceInterpretation.SUPPORTING, EvidenceInterpretation.FALSIFYING}
            and freshness > 0.0
        )
        effective_weight = request.strength * freshness if applied else 0.0

        confidence_after = current.confidence
        uncertainty_after = current.uncertainty
        evidence_count_after = current.evidence_count
        resulting_version = current.state_version
        policy_rationale = self._policy_rationale(request.interpretation, freshness)

        if applied:
            step = self.learning_rate * effective_weight
            if request.interpretation is EvidenceInterpretation.SUPPORTING:
                confidence_after = current.confidence + step * (1.0 - current.confidence)
            else:
                confidence_after = current.confidence * (1.0 - step)
            uncertainty_after = current.uncertainty * (1.0 - step)
            evidence_count_after = current.evidence_count + 1
            resulting_version = current.state_version + 1

            latest_observed_at = evidence.observed_at
            if current.last_evidence_at is not None:
                latest_observed_at = max(current.last_evidence_at, evidence.observed_at)

            state = current.model_copy(
                update={
                    "confidence": confidence_after,
                    "uncertainty": uncertainty_after,
                    "evidence_count": evidence_count_after,
                    "valid_from": request.evaluated_at,
                    "last_evidence_at": latest_observed_at,
                    "freshness": freshness_weight(
                        hypothesis.freshness_policy,
                        latest_observed_at,
                        request.evaluated_at,
                    ),
                    "state_version": resulting_version,
                    "updated_at": request.evaluated_at,
                }
            )
        else:
            state = current.model_copy(deep=True)

        update = BeliefUpdateRecord(
            hypothesis_id=hypothesis.id,
            evidence_id=evidence.id,
            interpretation=request.interpretation,
            strength=request.strength,
            interpretation_rationale=request.rationale,
            policy_name=self.name,
            policy_version=self.version,
            evidence_class=evidence.evidence_class,
            freshness_weight=freshness,
            effective_weight=effective_weight,
            prior_state_version=current.state_version,
            resulting_state_version=resulting_version,
            confidence_before=current.confidence,
            confidence_after=confidence_after,
            uncertainty_before=current.uncertainty,
            uncertainty_after=uncertainty_after,
            evidence_count_before=current.evidence_count,
            evidence_count_after=evidence_count_after,
            applied=applied,
            policy_rationale=policy_rationale,
            evaluated_at=request.evaluated_at,
        )
        return BeliefUpdateResult(state=state, update=update)

    @staticmethod
    def _validate_interpretation(
        evidence: EvidenceRecord,
        interpretation: EvidenceInterpretation,
    ) -> None:
        if evidence.evidence_class is EvidenceClass.TECHNICAL:
            if interpretation not in {
                EvidenceInterpretation.TECHNICAL,
                EvidenceInterpretation.NEUTRAL,
            }:
                raise ValueError(
                    "technical evidence cannot support or falsify an economic hypothesis"
                )
            return

        if interpretation is EvidenceInterpretation.TECHNICAL:
            raise ValueError("non-technical evidence cannot use technical interpretation")

    @staticmethod
    def _policy_rationale(
        interpretation: EvidenceInterpretation,
        freshness: float,
    ) -> str:
        if interpretation is EvidenceInterpretation.TECHNICAL:
            return "technical evidence is recorded without changing economic belief"
        if interpretation is EvidenceInterpretation.NEUTRAL:
            return "neutral evidence is recorded without changing belief state"
        if freshness == 0.0:
            return "evidence is outside the hypothesis freshness window"
        return "bounded deterministic update from explicit evidence interpretation"
