from __future__ import annotations

from pydantic import BaseModel, Field


class SignalVector(BaseModel):
    """Cross-business normalized evidence projection.

    Raw platform metrics remain persisted separately. Values in [0, 1] are
    relative/normalized evidence, ideally computed against a relevant baseline
    rather than universal thresholds.
    """

    attention: float | None = Field(default=None, ge=0.0, le=1.0)
    retention: float | None = Field(default=None, ge=0.0, le=1.0)
    engagement: float | None = Field(default=None, ge=0.0, le=1.0)
    intent: float | None = Field(default=None, ge=0.0, le=1.0)
    conversion: float | None = Field(default=None, ge=0.0, le=1.0)

    revenue: float = 0.0
    gross_profit: float | None = None
    currency: str = "USD"

    external_observations: int = Field(default=0, ge=0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    baseline_sample_size: int = Field(default=0, ge=0)

    def strongest_nonfinancial_signal(self) -> float | None:
        values = [
            value
            for value in (
                self.attention,
                self.retention,
                self.engagement,
                self.intent,
                self.conversion,
            )
            if value is not None
        ]
        return max(values) if values else None

    def has_financial_signal(self) -> bool:
        return self.revenue > 0 or (self.gross_profit is not None and self.gross_profit != 0)


class BaselineKey(BaseModel):
    """Defines the comparison cohort used to normalize raw platform metrics."""

    platform: str
    channel_id: str | None = None
    business_family: str | None = None
    content_format: str | None = None
    account_age_bucket: str | None = None
    geography: str | None = None
    language: str | None = None
