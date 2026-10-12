from __future__ import annotations

import json

from business_master.domain.enums import EvidenceClass, EvidenceProvenance, HypothesisType
from business_master.domain.evidence import EvidenceRecord
from business_master.domain.hypotheses import EconomicHypothesis
from business_master.optimization import (
    ConstraintOperator,
    ObjectiveSpec,
    OptimizationSpec,
    OutcomeConstraintSpec,
    ParameterKind,
    ParameterSpec,
    ParameterValueType,
    RandomOptimizationEngine,
    TrialObservation,
)


def evaluate(parameters: dict[str, float | int | str | bool]) -> dict[str, float]:
    """Deterministic synthetic market used only to demonstrate the closed loop."""
    price = float(parameters["price"])
    offer = str(parameters["offer"])
    creative = str(parameters["creative"])

    demand = max(0.0, 120.0 - price)
    if offer == "bundle":
        demand *= 1.12
    if creative == "B":
        demand *= 1.08
    elif creative == "C":
        demand *= 0.94

    contribution_margin = demand * max(0.0, price - 32.0) / 100.0
    refund_rate = 0.018 + max(0.0, price - 85.0) * 0.0015
    if offer == "bundle":
        refund_rate += 0.006

    return {
        "contribution_margin": contribution_margin,
        "refund_rate": refund_rate,
    }


def main() -> None:
    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.PRICING,
        subject="synthetic product pricing",
        proposition="price, offer, and creative jointly affect contribution margin",
        mechanism="search a bounded commercial parameter space under a refund constraint",
    )
    spec = OptimizationSpec(
        name="pricing-offer-creative",
        hypothesis_id=hypothesis.id,
        parameters=(
            ParameterSpec(
                name="price",
                kind=ParameterKind.RANGE,
                value_type=ParameterValueType.FLOAT,
                lower=59.0,
                upper=99.0,
            ),
            ParameterSpec(
                name="offer",
                kind=ParameterKind.CHOICE,
                value_type=ParameterValueType.STR,
                values=("plain", "bundle"),
            ),
            ParameterSpec(
                name="creative",
                kind=ParameterKind.CHOICE,
                value_type=ParameterValueType.STR,
                values=("A", "B", "C"),
            ),
        ),
        objectives=(ObjectiveSpec(metric="contribution_margin"),),
        outcome_constraints=(
            OutcomeConstraintSpec(
                metric="refund_rate",
                operator=ConstraintOperator.LE,
                bound=0.04,
            ),
        ),
        seed=42,
    )

    engine = RandomOptimizationEngine()
    run = engine.create_run(spec)
    evidence_ids: list[str] = []
    for suggestion in engine.suggest(run.id, count=30):
        metrics = evaluate(suggestion.parameters)
        evidence = EvidenceRecord(
            evidence_class=EvidenceClass.ECONOMIC,
            provenance=EvidenceProvenance.OBSERVED_OWN,
            kind="synthetic_trial_outcome",
            source="pricing_optimization_example",
            subject_type="economic_hypothesis",
            subject_id=hypothesis.id,
            features=metrics,
        )
        evidence_ids.append(str(evidence.id))
        engine.observe(
            TrialObservation(
                run_id=run.id,
                trial_id=suggestion.trial_id,
                metrics=metrics,
                evidence_ids=(evidence.id,),
            )
        )

    result = engine.best(run.id)
    assert result is not None
    output = {
        "hypothesis_id": str(hypothesis.id),
        "optimization_run_id": str(run.id),
        "evidence_count": len(evidence_ids),
        "result": result.model_dump(mode="json"),
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
