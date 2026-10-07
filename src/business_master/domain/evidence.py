from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from business_master.domain.clock import utcnow
from business_master.domain.enums import (
    EvidenceClass,
    EvidenceProvenance,
    EvidenceTargetKind,
)


class EvidenceRef(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    kind: str
    source: str
    observed_at: datetime = Field(default_factory=utcnow)
    entity_id: UUID | None = None
    features: dict[str, float | int | str | bool | None] = Field(default_factory=dict)
    payload_ref: str | None = None


type EvidenceScalar = float | int | str | bool | None


class EvidenceRecord(BaseModel):
    """Immutable V2 evidence item with explicit class, provenance and lineage."""

    id: UUID = Field(default_factory=uuid4)
    evidence_class: EvidenceClass
    provenance: EvidenceProvenance
    kind: str = Field(min_length=1)
    source: str = Field(min_length=1)
    source_event_id: str | None = Field(default=None, min_length=1)
    subject_type: str | None = Field(default=None, min_length=1)
    subject_id: UUID | None = None
    observed_at: datetime = Field(default_factory=utcnow)
    ingested_at: datetime = Field(default_factory=utcnow)
    features: dict[str, EvidenceScalar] = Field(default_factory=dict)
    payload_ref: str | None = None
    input_evidence_ids: list[UUID] = Field(default_factory=list)
    schema_version: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_record(self) -> Self:
        has_subject_type = self.subject_type is not None
        has_subject_id = self.subject_id is not None
        if has_subject_type != has_subject_id:
            raise ValueError("subject_type and subject_id must be provided together")

        if len(set(self.input_evidence_ids)) != len(self.input_evidence_ids):
            raise ValueError("input_evidence_ids cannot contain duplicates")
        if self.id in self.input_evidence_ids:
            raise ValueError("an evidence record cannot derive from itself")

        derived = self.provenance in {
            EvidenceProvenance.CALCULATED,
            EvidenceProvenance.INFERRED,
        }
        if derived and not self.input_evidence_ids:
            raise ValueError("calculated or inferred evidence requires input_evidence_ids")
        if not derived and self.input_evidence_ids:
            raise ValueError("observed or claimed evidence cannot declare derived inputs")
        return self

    @classmethod
    def from_legacy(
        cls,
        evidence: EvidenceRef,
        *,
        evidence_class: EvidenceClass,
        provenance: EvidenceProvenance,
        subject_type: str | None = None,
    ) -> Self:
        """Convert a V0 reference only when semantic classification is explicit."""

        if evidence.entity_id is not None and subject_type is None:
            raise ValueError("subject_type is required when legacy evidence has entity_id")
        if evidence.entity_id is None and subject_type is not None:
            raise ValueError("subject_type cannot be set when legacy evidence has no entity_id")

        return cls(
            id=evidence.id,
            evidence_class=evidence_class,
            provenance=provenance,
            kind=evidence.kind,
            source=evidence.source,
            subject_type=subject_type,
            subject_id=evidence.entity_id,
            observed_at=evidence.observed_at,
            features=evidence.features,
            payload_ref=evidence.payload_ref,
        )


class EvidenceAssociation(BaseModel):
    """Additive link from immutable evidence to a decision-relevant target."""

    evidence_id: UUID
    target_kind: EvidenceTargetKind
    target_id: UUID
    linked_at: datetime = Field(default_factory=utcnow)
