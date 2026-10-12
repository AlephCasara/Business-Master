from __future__ import annotations

import pytest

pytest.importorskip("ax")

from business_master.adapters.optimization.ax import AxOptimizationEngine
from business_master.optimization import (
    ObjectiveSpec,
    OptimizationSpec,
    ParameterKind,
    ParameterSpec,
    ParameterValueType,
    TrialObservation,
)


def test_ax_adapter_completes_one_observed_trial() -> None:
    engine = AxOptimizationEngine(method="fast")
    run = engine.create_run(
        OptimizationSpec(
            name="ax-smoke",
            parameters=(
                ParameterSpec(
                    name="x",
                    kind=ParameterKind.RANGE,
                    value_type=ParameterValueType.FLOAT,
                    lower=0.0,
                    upper=1.0,
                ),
            ),
            objectives=(ObjectiveSpec(metric="value"),),
            seed=11,
        )
    )

    suggestion = engine.suggest(run.id)[0]
    x = float(suggestion.parameters["x"])
    engine.observe(
        TrialObservation(
            run_id=run.id,
            trial_id=suggestion.trial_id,
            metrics={"value": 1.0 - abs(x - 0.75)},
        )
    )

    result = engine.best(run.id)

    assert result is not None
    assert result.candidates[0].trial_id == suggestion.trial_id
    assert run.engine_name == "ax"
    assert run.engine_version != "unknown"
