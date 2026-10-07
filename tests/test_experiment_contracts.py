from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from business_master.domain.enums import (
    ComparisonOperator,
    EvidenceClass,
    MetricAggregation,
)
from business_master.domain.experiment_contracts import (
    ExperimentBudget,
    ExperimentContract,
    MeasurementContract,
    MetricCriterion,
)


def _criterion(metric: str = "external_clicks") -> MetricCriterion:
    return MetricCriterion(
        metric=metric,
        operator=ComparisonOperator.GTE,
        threshold=1.0,
        evidence_class=EvidenceClass.MARKET,
        aggregation=MetricAggregation.SUM,
    )


def _measurement() -> MeasurementContract:
    return MeasurementContract(
        window_seconds=86400,
        primary_metric="external_clicks",
        supporting_criteria=[_criterion()],
        falsifying_criteria=[
            MetricCriterion(
                metric="external_clicks",
                operator=ComparisonOperator.EQ,
                threshold=0.0,
                evidence_class=EvidenceClass.MARKET,
                aggregation=MetricAggregation.SUM,
                minimum_observations=3,
            )
        ],
        minimum_external_observations=3,
    )


def test_measurement_contract_requires_machine_readable_primary_metric() -> None:
    with pytest.raises(ValidationError):
        MeasurementContract(window_seconds=60, primary_metric="views")

    with pytest.raises(ValidationError):
        MeasurementContract(
            window_seconds=60,
            primary_metric="views",
            supporting_criteria=[_criterion("clicks")],
        )


def test_experiment_contract_separates_market_evidence_from_resource_budget() -> None:
    contract = ExperimentContract(
        economic_hypothesis_id=uuid4(),
        business_family="content",
        question="Does this hook generate external commercial intent?",
        intervention_dimensions={"hook": "price-anchor"},
        held_constant_dimensions=["topic", "visual_grammar"],
        expected_observation="At least one attributed external click inside 24 hours.",
        falsification_condition="No attributed clicks after the completed evidence window.",
        measurement=_measurement(),
    )

    assert contract.measurement.supporting_criteria[0].evidence_class is EvidenceClass.MARKET
    assert contract.budget.max_cash_cost == 0.0
    assert contract.budget.max_attempts == 1
    assert contract.budget.max_external_actions == 1


def test_experiment_contract_rejects_ambiguous_dimension_control() -> None:
    with pytest.raises(ValidationError):
        ExperimentContract(
            economic_hypothesis_id=uuid4(),
            business_family="content",
            question="Does hook B beat the baseline?",
            intervention_dimensions={"hook": "B"},
            held_constant_dimensions=["hook"],
            expected_observation="Higher click signal.",
            falsification_condition="No higher click signal.",
            measurement=_measurement(),
        )


def test_experiment_contract_rejects_self_lineage() -> None:
    contract_id = uuid4()
    with pytest.raises(ValidationError):
        ExperimentContract(
            id=contract_id,
            economic_hypothesis_id=uuid4(),
            business_family="b2b",
            question="Does the offer earn a positive reply?",
            expected_observation="A qualified positive reply.",
            falsification_condition="No positive reply after the measurement window.",
            measurement=_measurement(),
            budget=ExperimentBudget(max_human_minutes=5.0),
            parent_contract_id=contract_id,
        )
