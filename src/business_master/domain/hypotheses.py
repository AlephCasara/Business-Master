from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from business_master.domain.clock import utcnow
from business_master.domain.enums import EvidenceTier


class Hypothesis(BaseModel):
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
