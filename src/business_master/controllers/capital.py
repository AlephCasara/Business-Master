from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from business_master.domain.capital import (
    CapitalAuthorization,
    CapitalAuthorizationRequest,
    CapitalEnvelope,
)
from business_master.policies.capital import CapitalPolicy


class CapitalStore(Protocol):
    def authorize(
        self,
        request: CapitalAuthorizationRequest,
        envelope: CapitalEnvelope,
        *,
        policy: CapitalPolicy = CapitalPolicy(),
    ) -> CapitalAuthorization: ...


@dataclass(slots=True)
class CapitalController:
    """Authorize bounded capital without dispatching work or recording spend."""

    store: CapitalStore
    policy: CapitalPolicy = CapitalPolicy()

    def authorize(
        self,
        request: CapitalAuthorizationRequest,
        envelope: CapitalEnvelope,
    ) -> CapitalAuthorization:
        return self.store.authorize(request, envelope, policy=self.policy)
