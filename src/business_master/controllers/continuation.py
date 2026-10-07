from __future__ import annotations

from business_master.domain.decisions import (
    AutonomousContinuationRequest,
    AutonomousContinuationResult,
)
from business_master.policies.continuation import ContinuationPolicy
from business_master.storage.continuation_postgres import PostgresContinuationStore


class ContinuationController:
    """Thin application boundary for persisted autonomous continuation."""

    def __init__(
        self,
        store: PostgresContinuationStore,
        *,
        policy: ContinuationPolicy | None = None,
    ) -> None:
        self._store = store
        self._policy = policy or ContinuationPolicy()

    def continue_from(
        self,
        request: AutonomousContinuationRequest,
    ) -> AutonomousContinuationResult:
        return self._store.continue_from(request, policy=self._policy)
