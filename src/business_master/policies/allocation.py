from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from business_master.domain.enums import EvidenceTier


@dataclass(frozen=True, slots=True)
class AllocationCandidate:
    """Legacy V0 scalar-allocation candidate kept for compatibility tests/callers."""

    entity_id: UUID
    tier: EvidenceTier
    priority: float


@dataclass(frozen=True, slots=True)
class Allocation:
    """Legacy V0 scalar allocation result; not a V2 resource/capital authorization."""

    entity_id: UUID
    units: float
    reason: str


@dataclass(frozen=True, slots=True)
class AllocationPolicy:
    """Legacy V0 bounded exploration/exploitation allocator.

    ``total_units`` is intentionally a scalar compatibility abstraction. New V2
    portfolio/capital control must reason over ResourceVector availability and
    authoritative ledger state instead of extending this policy.
    """

    exploration_fraction: float = 0.20
    max_candidate_fraction: float = 0.50

    def allocate(
        self,
        candidates: list[AllocationCandidate],
        total_units: float,
    ) -> list[Allocation]:
        if total_units <= 0 or not candidates:
            return []

        live = [c for c in candidates if c.tier not in {EvidenceTier.KILLED, EvidenceTier.PAUSED}]
        if not live:
            return []

        probes = [c for c in live if c.tier == EvidenceTier.PROBE]
        mature = [c for c in live if c.tier in {EvidenceTier.PILOT, EvidenceTier.SCALE}]

        exploration_units = total_units * self.exploration_fraction if probes else 0.0
        exploitation_units = total_units - exploration_units

        result: dict[UUID, float] = {c.entity_id: 0.0 for c in live}

        if probes and exploration_units > 0:
            per_probe = exploration_units / len(probes)
            for candidate in probes:
                result[candidate.entity_id] += per_probe

        exploitation_pool = mature if mature else live
        self._weighted_add(result, exploitation_pool, exploitation_units)

        cap = total_units * self.max_candidate_fraction
        overflow = 0.0
        for entity_id, units in list(result.items()):
            if units > cap:
                overflow += units - cap
                result[entity_id] = cap

        # Redistribute cap overflow to candidates that still have room.
        while overflow > 1e-9:
            eligible = [entity_id for entity_id, units in result.items() if units < cap - 1e-9]
            if not eligible:
                break
            share = overflow / len(eligible)
            moved = 0.0
            for entity_id in eligible:
                room = cap - result[entity_id]
                delta = min(room, share)
                result[entity_id] += delta
                moved += delta
            if moved <= 1e-12:
                break
            overflow -= moved

        return [
            Allocation(
                entity_id=c.entity_id,
                units=result[c.entity_id],
                reason=(
                    "exploration+weighted exploitation"
                    if c.tier == EvidenceTier.PROBE
                    else "weighted exploitation"
                ),
            )
            for c in live
            if result[c.entity_id] > 0
        ]

    @staticmethod
    def _weighted_add(
        target: dict[UUID, float],
        candidates: list[AllocationCandidate],
        units: float,
    ) -> None:
        if units <= 0 or not candidates:
            return
        weights = [max(c.priority, 0.0) for c in candidates]
        weight_sum = sum(weights)
        if weight_sum <= 0:
            equal = units / len(candidates)
            for candidate in candidates:
                target[candidate.entity_id] += equal
            return
        for candidate, weight in zip(candidates, weights, strict=True):
            target[candidate.entity_id] += units * (weight / weight_sum)
