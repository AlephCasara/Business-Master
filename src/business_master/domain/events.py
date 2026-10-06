from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from business_master.domain.models import utcnow

EventName = Literal[
    "market.observation.created",
    "hypothesis.created",
    "hypothesis.updated",
    "experiment.created",
    "experiment.started",
    "experiment.externalized",
    "experiment.completed",
    "metric.snapshot.created",
    "business.outcome.created",
    "experiment.scored",
    "decision.created",
    "creative.requested",
    "creative.rendered",
    "creative.qc_passed",
    "creative.qc_failed",
    "resource.available",
    "resource.unavailable",
    "human_action.requested",
    "human_action.resolved",
    "reconcile.requested",
]


class DomainEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: EventName
    aggregate_type: str
    aggregate_id: UUID
    occurred_at: datetime = Field(default_factory=utcnow)
    causation_id: UUID | None = None
    correlation_id: UUID = Field(default_factory=uuid4)
    payload: dict[str, Any] = Field(default_factory=dict)
    schema_version: int = 1


class EventEnvelope(BaseModel):
    """Transport-neutral wrapper used by in-memory, Hatchet and future runtimes."""

    event: DomainEvent
    attempts: int = 0
    received_at: datetime = Field(default_factory=utcnow)
