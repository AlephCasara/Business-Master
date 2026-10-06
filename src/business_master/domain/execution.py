from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from business_master.domain.clock import utcnow
from business_master.domain.enums import SignalKind


class ExecutionResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    experiment_id: UUID | None = None
    success: bool
    signal_kind: SignalKind
    started_at: datetime
    completed_at: datetime = Field(default_factory=utcnow)
    wall_seconds: float = 0.0
    cpu_seconds: float | None = None
    gpu_seconds: float | None = None
    model_tokens: int | None = None
    retries: int = 0
    human_minutes: float = 0.0
    cash_cost: float = 0.0
    error_code: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
