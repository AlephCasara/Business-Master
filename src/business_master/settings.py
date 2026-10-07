from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "local"
    database_url: str = "postgresql://business_master:business_master@127.0.0.1:5432/business_master"
    asset_root: Path = Path("./var/assets")

    # Operator-configured bootstrap safety ceilings only. They are not cash balances,
    # financial authority, or spend authorization. Portfolio/capital policy must
    # intersect these ceilings with authoritative ledger state before paid execution.
    paid_ads_budget_daily: float = Field(default=0.0, ge=0.0)
    external_ai_api_budget_daily: float = Field(default=0.0, ge=0.0)
    cloud_gpu_budget_daily: float = Field(default=0.0, ge=0.0)
    paid_saas_budget_daily: float = Field(default=0.0, ge=0.0)

    exploration_fraction: float = Field(default=0.20, ge=0.0, le=1.0)
    max_candidate_allocation_fraction: float = Field(default=0.50, gt=0.0, le=1.0)
    max_reconcile_actions: int = Field(default=100, ge=1)

    # Optional local OpenAI-compatible endpoint. Empty means deterministic-only bootstrap.
    local_model_base_url: str | None = None
    local_model_name: str | None = None

    # Human is an expensive/rare resource. Batch non-urgent requests.
    human_batch_interval_seconds: int = Field(default=3600, ge=60)

    def paid_spend_hard_ceilings(self) -> dict[str, float]:
        """Return operator safety ceilings without implying available financial capacity."""

        return {
            "paid_ads": self.paid_ads_budget_daily,
            "external_ai_api": self.external_ai_api_budget_daily,
            "cloud_gpu": self.cloud_gpu_budget_daily,
            "paid_saas": self.paid_saas_budget_daily,
        }

    def ensure_local_directories(self) -> None:
        self.asset_root.mkdir(parents=True, exist_ok=True)
