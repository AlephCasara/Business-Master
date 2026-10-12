from __future__ import annotations

from typing import Protocol
from uuid import UUID

from business_master.optimization.models import (
    OptimizationResult,
    OptimizationRun,
    OptimizationSpec,
    TrialObservation,
    TrialSuggestion,
)


class OptimizationEngine(Protocol):
    name: str
    version: str

    def create_run(
        self,
        spec: OptimizationSpec,
        *,
        run_id: UUID | None = None,
    ) -> OptimizationRun: ...

    def suggest(self, run_id: UUID, *, count: int = 1) -> list[TrialSuggestion]: ...

    def observe(self, observation: TrialObservation) -> None: ...

    def best(self, run_id: UUID) -> OptimizationResult | None: ...
