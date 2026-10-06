from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from business_master.domain.enums import DecisionType, RiskLevel
from business_master.domain.models import Decision
from business_master.domain.signals import SignalVector


@dataclass(frozen=True, slots=True)
class FeedbackPolicy:
    """Converts normalized external evidence into the next bounded decision.

    This policy deliberately never returns SCALE. Scaling is a separate graduation/allocation
    decision that requires replication.
    """

    version: str = "0.1"
    positive_threshold: float = 0.80
    negative_threshold: float = 0.20
    minimum_baseline_sample: int = 10

    def decide(
        self,
        *,
        experiment_id: UUID,
        signal: SignalVector,
        measurement_window_complete: bool,
        evidence_ids: list[UUID] | None = None,
    ) -> Decision | None:
        evidence_ids = evidence_ids or []
        features = signal.model_dump(mode="json")

        if signal.gross_profit is not None and signal.gross_profit > 0:
            return self._mutation(
                experiment_id,
                evidence_ids,
                features,
                "Positive gross-profit evidence justifies a bounded child mutation.",
            )

        if signal.revenue > 0:
            return self._mutation(
                experiment_id,
                evidence_ids,
                features,
                "First revenue evidence justifies replication/mutation, not unbounded scale.",
            )

        strongest = signal.strongest_nonfinancial_signal()
        baseline_ready = signal.baseline_sample_size >= self.minimum_baseline_sample

        if baseline_ready and strongest is not None and strongest >= self.positive_threshold:
            return self._mutation(
                experiment_id,
                evidence_ids,
                features,
                "High cohort-relative external signal justifies a bounded child mutation.",
            )

        # Cold start: real external interaction is valuable evidence even before a stable baseline exists.
        if signal.external_observations > 0 and not baseline_ready:
            return self._mutation(
                experiment_id,
                evidence_ids,
                features,
                "Real external traction arrived during cold start; create a bounded replication to build baseline.",
            )

        if measurement_window_complete:
            if strongest is None or strongest <= self.negative_threshold:
                return self._mutation(
                    experiment_id,
                    evidence_ids,
                    features,
                    "Measurement window completed with weak/no signal; mutate materially rather than repeating blindly.",
                )
            return Decision(
                entity_id=experiment_id,
                decision_type=DecisionType.CONTINUE,
                policy_name="feedback",
                policy_version=self.version,
                evidence_ids=evidence_ids,
                observed_features=features,
                risk=RiskLevel.ZERO,
                rationale="Evidence is non-terminal but not strong enough for winner replication yet.",
            )

        return None

    def _mutation(
        self,
        experiment_id: UUID,
        evidence_ids: list[UUID],
        features: dict[str, object],
        rationale: str,
    ) -> Decision:
        return Decision(
            entity_id=experiment_id,
            decision_type=DecisionType.MUTATE,
            policy_name="feedback",
            policy_version=self.version,
            evidence_ids=evidence_ids,
            observed_features=features,
            risk=RiskLevel.LOW,
            rationale=rationale,
        )
