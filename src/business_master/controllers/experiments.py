from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from business_master.domain.enums import EvidenceTier, ExperimentStatus
from business_master.domain.models import Experiment, Hypothesis, MutationSpec


@dataclass(frozen=True, slots=True)
class ExperimentController:
    """Pure experiment construction and lineage rules."""

    def create_probe(
        self,
        hypothesis: Hypothesis,
        *,
        business_family: str | None = None,
        dimensions: dict[str, Any] | None = None,
        expected_compute_units: float = 0.0,
        expected_human_minutes: float = 0.0,
    ) -> Experiment:
        if not hypothesis.active:
            raise ValueError("cannot create a probe for an inactive hypothesis")
        if hypothesis.tier in {EvidenceTier.PAUSED, EvidenceTier.KILLED}:
            raise ValueError(f"cannot create a probe for hypothesis tier={hypothesis.tier}")

        return Experiment(
            hypothesis_id=hypothesis.id,
            status=ExperimentStatus.PLANNED,
            tier=EvidenceTier.PROBE,
            business_family=business_family or hypothesis.family,
            dimensions=deepcopy(dimensions or {}),
            expected_cash_cost=0.0,
            expected_compute_units=max(expected_compute_units, 0.0),
            expected_human_minutes=max(expected_human_minutes, 0.0),
        )

    def mutate(
        self,
        parent: Experiment,
        *,
        changed_dimensions: dict[str, Any],
        rationale: str,
        preserve_dimensions: tuple[str, ...] = (),
        expected_compute_units: float | None = None,
        expected_human_minutes: float | None = None,
    ) -> Experiment:
        if not changed_dimensions:
            raise ValueError("a mutation must change at least one dimension")
        if parent.tier in {EvidenceTier.PAUSED, EvidenceTier.KILLED}:
            raise ValueError(f"cannot mutate parent tier={parent.tier}")

        overlap = set(changed_dimensions).intersection(preserve_dimensions)
        if overlap:
            raise ValueError(f"dimensions cannot be both changed and preserved: {sorted(overlap)}")

        new_dimensions = deepcopy(parent.dimensions)
        new_dimensions.update(deepcopy(changed_dimensions))

        mutation = MutationSpec(
            parent_experiment_id=parent.id,
            changed_dimensions=deepcopy(changed_dimensions),
            preserved_dimensions=list(preserve_dimensions),
            rationale=rationale,
        )

        # Children remain bounded to the parent's current evidence tier. Graduation is
        # a separate policy decision and cannot happen implicitly through mutation.
        return Experiment(
            hypothesis_id=parent.hypothesis_id,
            parent_id=parent.id,
            status=ExperimentStatus.PLANNED,
            tier=parent.tier,
            business_family=parent.business_family,
            channel_id=parent.channel_id,
            product_id=parent.product_id,
            mutation=mutation,
            dimensions=new_dimensions,
            expected_cash_cost=0.0,
            expected_compute_units=(
                parent.expected_compute_units
                if expected_compute_units is None
                else max(expected_compute_units, 0.0)
            ),
            expected_human_minutes=(
                parent.expected_human_minutes
                if expected_human_minutes is None
                else max(expected_human_minutes, 0.0)
            ),
        )
