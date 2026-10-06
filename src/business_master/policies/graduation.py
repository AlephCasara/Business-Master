from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from business_master.domain.enums import DecisionType, EvidenceTier, RiskLevel
from business_master.domain.models import Decision


@dataclass(frozen=True, slots=True)
class GraduationEvidence:
    external_observations: int = 0
    positive_signals: int = 0
    negative_signals: int = 0
    replicated_winners: int = 0
    distinct_contexts: int = 0
    revenue: float = 0.0
    gross_profit: float = 0.0
    technical_failures: int = 0
    policy_blocks: int = 0
    severe_risk_events: int = 0


@dataclass(frozen=True, slots=True)
class GraduationPolicy:
    """Economic graduation policy inspired by Probe/Pilot/Scale, not trading thresholds."""

    version: str = "0.1"
    probe_to_pilot_external_observations: int = 2
    probe_to_pilot_positive_signals: int = 1
    probe_to_pilot_replications: int = 1
    pilot_to_scale_external_observations: int = 5
    pilot_to_scale_positive_signals: int = 3
    pilot_to_scale_replications: int = 2
    pilot_to_scale_distinct_contexts: int = 2
    kill_negative_signals: int = 5

    def decide(
        self,
        *,
        entity_id: UUID,
        current_tier: EvidenceTier,
        evidence: GraduationEvidence,
        evidence_ids: list[UUID] | None = None,
    ) -> Decision | None:
        evidence_ids = evidence_ids or []
        features = {
            "external_observations": evidence.external_observations,
            "positive_signals": evidence.positive_signals,
            "negative_signals": evidence.negative_signals,
            "replicated_winners": evidence.replicated_winners,
            "distinct_contexts": evidence.distinct_contexts,
            "revenue": evidence.revenue,
            "gross_profit": evidence.gross_profit,
            "technical_failures": evidence.technical_failures,
            "policy_blocks": evidence.policy_blocks,
            "severe_risk_events": evidence.severe_risk_events,
        }

        if evidence.severe_risk_events > 0:
            return Decision(
                entity_id=entity_id,
                decision_type=DecisionType.PAUSE,
                policy_name="graduation",
                policy_version=self.version,
                evidence_ids=evidence_ids,
                observed_features=features,
                risk=RiskLevel.HIGH,
                rationale="Severe risk evidence requires pause before further allocation.",
            )

        if current_tier in {EvidenceTier.PAUSED, EvidenceTier.KILLED}:
            return None

        if (
            evidence.negative_signals >= self.kill_negative_signals
            and evidence.positive_signals == 0
        ):
            return Decision(
                entity_id=entity_id,
                decision_type=DecisionType.KILL,
                policy_name="graduation",
                policy_version=self.version,
                evidence_ids=evidence_ids,
                observed_features=features,
                risk=RiskLevel.LOW,
                rationale=(
                    "Repeated external negative signal with no positive replication no longer "
                    "clears opportunity cost. Preserve lineage for future descendants."
                ),
            )

        if current_tier == EvidenceTier.PROBE:
            if (
                evidence.external_observations >= self.probe_to_pilot_external_observations
                and evidence.positive_signals >= self.probe_to_pilot_positive_signals
                and evidence.replicated_winners >= self.probe_to_pilot_replications
            ):
                return Decision(
                    entity_id=entity_id,
                    decision_type=DecisionType.GRADUATE,
                    policy_name="graduation",
                    policy_version=self.version,
                    evidence_ids=evidence_ids,
                    observed_features=features,
                    risk=RiskLevel.LOW,
                    rationale="Probe signal replicated enough to justify bounded Pilot allocation.",
                )
            return None

        if current_tier == EvidenceTier.PILOT:
            if (
                evidence.external_observations >= self.pilot_to_scale_external_observations
                and evidence.positive_signals >= self.pilot_to_scale_positive_signals
                and evidence.replicated_winners >= self.pilot_to_scale_replications
                and evidence.distinct_contexts >= self.pilot_to_scale_distinct_contexts
            ):
                return Decision(
                    entity_id=entity_id,
                    decision_type=DecisionType.GRADUATE,
                    policy_name="graduation",
                    policy_version=self.version,
                    evidence_ids=evidence_ids,
                    observed_features=features,
                    risk=RiskLevel.MEDIUM,
                    rationale=(
                        "Pilot signal replicated across enough observations and contexts to "
                        "justify Scale allocation."
                    ),
                )
            return None

        return None


def next_tier(current: EvidenceTier, decision: Decision | None) -> EvidenceTier:
    if decision is None:
        return current
    if decision.decision_type == DecisionType.PAUSE:
        return EvidenceTier.PAUSED
    if decision.decision_type == DecisionType.KILL:
        return EvidenceTier.KILLED
    if decision.decision_type != DecisionType.GRADUATE:
        return current
    if current == EvidenceTier.PROBE:
        return EvidenceTier.PILOT
    if current == EvidenceTier.PILOT:
        return EvidenceTier.SCALE
    return current
