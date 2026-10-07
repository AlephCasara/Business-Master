from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from business_master.domain.beliefs import FreshnessPolicy
from business_master.domain.clock import utcnow
from business_master.domain.enums import (
    EvidenceTier,
    HypothesisStatus,
    HypothesisType,
)


class Hypothesis(BaseModel):
    """Legacy V0 hypothesis kept for strangler migration compatibility."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    thesis: str
    family: str
    market: str | None = None
    audience: str | None = None
    tier: EvidenceTier = EvidenceTier.PROBE
    parent_id: UUID | None = None
    evidence_ids: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    active: bool = True


class BeliefContext(BaseModel):
    market: str | None = None
    audience: str | None = None
    geography: str | None = None
    language: str | None = None
    channel: str | None = None
    dimensions: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class EvidenceRequirements(BaseModel):
    minimum_count: int = Field(default=1, ge=0)
    minimum_independent_sources: int = Field(default=1, ge=0)
    required_kinds: list[str] = Field(default_factory=list)


class EconomicHypothesis(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    hypothesis_type: HypothesisType
    subject: str
    proposition: str
    mechanism: str | None = None
    context: BeliefContext = Field(default_factory=BeliefContext)

    expected_observation: str | None = None
    falsification_condition: str | None = None
    evidence_requirements: EvidenceRequirements = Field(default_factory=EvidenceRequirements)
    measurement_window_seconds: int | None = Field(default=None, gt=0)
    freshness_policy: FreshnessPolicy = Field(default_factory=FreshnessPolicy)

    parent_ids: list[UUID] = Field(default_factory=list)
    dependency_ids: list[UUID] = Field(default_factory=list)
    legacy_hypothesis_id: UUID | None = None

    status: HypothesisStatus = HypothesisStatus.ACTIVE
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    @model_validator(mode="after")
    def validate_lineage(self) -> Self:
        if self.id in self.parent_ids or self.id in self.dependency_ids:
            raise ValueError("an economic hypothesis cannot depend on itself")
        if len(set(self.parent_ids)) != len(self.parent_ids):
            raise ValueError("parent_ids cannot contain duplicates")
        if len(set(self.dependency_ids)) != len(self.dependency_ids):
            raise ValueError("dependency_ids cannot contain duplicates")
        return self

    @classmethod
    def from_legacy(
        cls,
        legacy: Hypothesis,
        *,
        hypothesis_type: HypothesisType,
        subject: str | None = None,
        mechanism: str | None = None,
    ) -> EconomicHypothesis:
        """Convert a legacy hypothesis without guessing its economic semantics.

        The caller must explicitly classify the legacy record. Legacy parent IDs are
        intentionally not copied because they reference the legacy hypothesis table,
        not the new economic-hypothesis graph.
        """

        return cls(
            hypothesis_type=hypothesis_type,
            subject=subject or legacy.name,
            proposition=legacy.thesis,
            mechanism=mechanism,
            context=BeliefContext(
                market=legacy.market,
                audience=legacy.audience,
                dimensions={
                    "legacy_family": legacy.family,
                    "legacy_tier": legacy.tier.value,
                },
            ),
            legacy_hypothesis_id=legacy.id,
            status=HypothesisStatus.ACTIVE if legacy.active else HypothesisStatus.PAUSED,
            created_at=legacy.created_at,
            updated_at=legacy.updated_at,
        )
