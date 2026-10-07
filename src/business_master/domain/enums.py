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
    CASH = "cash"
    WORKING_CAPITAL = "working_capital"
    CPU = "cpu"
    GPU = "gpu"
    LLM = "llm"
    API_QUOTA = "api_quota"
    BROWSER = "browser"
    MOBILE = "mobile"
    HUMAN = "human"
    PLATFORM_SLOT = "platform_slot"
    ACCOUNT_CAPACITY = "account_capacity"


class ResourceReservationStatus(StrEnum):
    ACTIVE = "active"
    RELEASED = "released"


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


class HypothesisType(StrEnum):
    DEMAND = "demand"
    PAIN = "pain"
    AUDIENCE = "audience"
    ANGLE = "angle"
    HOOK = "hook"
    CREATIVE = "creative"
    OFFER = "offer"
    PRICING = "pricing"
    ACQUISITION = "acquisition"
    CHANNEL = "channel"
    FUNNEL = "funnel"
    AOV = "aov"
    LTV = "ltv"
    PRODUCT = "product"
    SUPPLY = "supply"
    FULFILLMENT = "fulfillment"
    B2B_PAIN = "b2b_pain"
    OUTREACH = "outreach"
    DELIVERY = "delivery"
    CAPABILITY = "capability"
    ASSET = "asset"


class HypothesisStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class FreshnessMode(StrEnum):
    NONE = "none"
    TTL = "ttl"
    LINEAR_DECAY = "linear_decay"
    EXPONENTIAL_DECAY = "exponential_decay"


class EvidenceClass(StrEnum):
    TECHNICAL = "technical"
    MARKET = "market"
    ECONOMIC = "economic"


class EvidenceProvenance(StrEnum):
    OBSERVED_OWN = "observed_own"
    OBSERVED_OFFICIAL_EXTERNAL = "observed_official_external"
    OBSERVED_PUBLIC = "observed_public"
    CALCULATED = "calculated"
    INFERRED = "inferred"
    CREATOR_CLAIM = "creator_claim"
    UNKNOWN = "unknown"


class EvidenceTargetKind(StrEnum):
    ECONOMIC_HYPOTHESIS = "economic_hypothesis"
    EXPERIMENT_CONTRACT = "experiment_contract"
    EXPERIMENT = "experiment"


class ComparisonOperator(StrEnum):
    LT = "lt"
    LTE = "lte"
    EQ = "eq"
    GTE = "gte"
    GT = "gt"


class MetricAggregation(StrEnum):
    LATEST = "latest"
    SUM = "sum"
    MEAN = "mean"
    MIN = "min"
    MAX = "max"
