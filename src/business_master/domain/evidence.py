from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from business_master.domain.clock import utcnow


class EvidenceRef(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    kind: str
    source: str
    observed_at: datetime = Field(default_factory=utcnow)
    entity_id: UUID | None = None
    features: dict[str, float | int | str | bool | None] = Field(default_factory=dict)
    payload_ref: str | None = None
