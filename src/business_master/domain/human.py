from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from business_master.domain.clock import utcnow
from business_master.domain.enums import RiskLevel


class HumanActionRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    action_type: str
    reason: str
    experiment_id: UUID | None = None
    account_id: UUID | None = None
    risk: RiskLevel = RiskLevel.HIGH
    required_by: datetime | None = None
    created_at: datetime = Field(default_factory=utcnow)
    resolved_at: datetime | None = None
