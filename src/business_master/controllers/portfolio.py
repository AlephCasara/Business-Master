from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from business_master.domain.portfolio import PortfolioPlan, PortfolioPlanRequest
from business_master.policies.portfolio import PortfolioPolicy


class PortfolioStore(Protocol):
    def save(self, plan: PortfolioPlan) -> PortfolioPlan: ...


@dataclass(slots=True)
class PortfolioController:
    """Bind pure portfolio policy to durable plan persistence without execution."""

    store: PortfolioStore
    policy: PortfolioPolicy = PortfolioPolicy()

    def plan_and_persist(self, request: PortfolioPlanRequest) -> PortfolioPlan:
        return self.store.save(self.policy.plan(request))
