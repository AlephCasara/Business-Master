from __future__ import annotations

from enum import StrEnum


class EvidenceTier(StrEnum):
    PROBE = "probe"
    PILOT = "pilot"
    SCALE = "scale"
    PAUSED = "paused"
    KILLED = "killed"


class SignalKind(StrEnum):
    TECHNICAL_FAILURE = "technical_failure"
    PLATFORM_FAILURE = "platform_failure"
    POLICY_BLOCK = "policy_block"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    NO_SIGNAL = "no_signal"
    NEGATIVE_SIGNAL = "negative_signal"
    POSITIVE_SIGNAL = "positive_signal"


class DecisionType(StrEnum):
    CREATE_PROBE = "create_probe"
    MUTATE = "mutate"
    CONTINUE = "continue"
    PAUSE = "pause"
    KILL = "kill"
    GRADUATE = "graduate"
    SCALE_ALLOCATION = "scale_allocation"
    REDUCE_ALLOCATION = "reduce_allocation"
    REQUEST_HUMAN = "request_human"


class ResourceKind(StrEnum):
    CPU = "cpu"
    GPU = "gpu"
    LLM = "llm"
    BROWSER = "browser"
    MOBILE = "mobile"
    HUMAN = "human"
    PLATFORM_SLOT = "platform_slot"


class RiskLevel(StrEnum):
    ZERO = "zero"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExperimentStatus(StrEnum):
    PLANNED = "planned"
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_EXTERNAL = "waiting_external"
    WAITING_HUMAN = "waiting_human"
    MEASURING = "measuring"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"
