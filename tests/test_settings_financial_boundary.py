from __future__ import annotations

from business_master.settings import Settings


def test_paid_spend_hard_ceilings_are_explicit_operator_caps() -> None:
    settings = Settings(
        paid_ads_budget_daily=10.0,
        external_ai_api_budget_daily=20.0,
        cloud_gpu_budget_daily=30.0,
        paid_saas_budget_daily=40.0,
    )

    assert settings.paid_spend_hard_ceilings() == {
        "paid_ads": 10.0,
        "external_ai_api": 20.0,
        "cloud_gpu": 30.0,
        "paid_saas": 40.0,
    }
