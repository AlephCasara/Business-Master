from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from business_master.domain.clock import utcnow
from business_master.domain.enums import ResourceKind


class Resource(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    kind: ResourceKind
    available: bool = True
    capacity: float = 1.0
    labels: dict[str, str | int | float | bool] = Field(default_factory=dict)
    last_seen_at: datetime = Field(default_factory=utcnow)
