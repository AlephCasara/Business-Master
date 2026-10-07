from __future__ import annotations

import os
from pathlib import Path

import psycopg
import pytest

from business_master.controllers.experiments import ExperimentController
from business_master.domain.enums import (
    ComparisonOperator,
    EvidenceClass,
    HypothesisType,
    MetricAggregation,
)
from business_master.domain.experiment_contracts import (
    ExperimentContract,
    ExperimentContractBinding,
    MeasurementContract,
    MetricCriterion,
)
from business_master.domain.hypotheses import EconomicHypothesis, Hypothesis
from business_master.storage.beliefs_postgres import PostgresBeliefStore
from business_master.storage.experiment_contracts_postgres import PostgresExperimentContractStore
from business_master.storage.postgres import PostgresStore


@pytest.fixture()
def postgres_dsn() -> str:
    dsn = os.environ.get("BM_TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("BM_TEST_DATABASE_URL is not configured")

    with psycopg.connect(dsn, autocommit=True) as conn:
        conn.execute("DROP SCHEMA IF EXISTS public CASCADE")
        conn.execute("CREATE SCHEMA public")
        migrations = sorted(Path("db/migrations").glob("*.sql"))
        for migration in migrations:
            statements = [
                statement.strip()
                for statement in migration.read_text().split(";")
                if statement.strip()
            ]
            for statement in statements:
                conn.execute(statement)

    return dsn


def _measurement() -> MeasurementContract:
    return MeasurementContract(
        window_seconds=86400,
        primary_metric="external_clicks",
        supporting_criteria=[
            MetricCriterion(
                metric="external_clicks",
                operator=ComparisonOperator.GTE,
                threshold=1.0,
                evidence_class=EvidenceClass.MARKET,
                aggregation=MetricAggregation.SUM,
            )
        ],
    )


def test_contract_roundtrip_binding_and_immutability(postgres_dsn: str) -> None:
    legacy_hypothesis = Hypothesis(
        name="chart-offer",
        thesis="A chart-based short can generate commercial intent",
        family="content",
        market="US",
        audience="retail investors",
    )
    v0_store = PostgresStore(postgres_dsn)
    v0_store.save_hypothesis(legacy_hypothesis)

    economic_hypothesis = EconomicHypothesis.from_legacy(
        legacy_hypothesis,
        hypothesis_type=HypothesisType.HOOK,
        mechanism="Use a concrete chart hook to create curiosity and an external click.",
    )
    belief_store = PostgresBeliefStore(postgres_dsn)
    belief_store.save_economic_hypothesis(economic_hypothesis)

    experiment = ExperimentController().create_probe(
        legacy_hypothesis,
        dimensions={"hook": "price-anchor", "topic": "consumer-finance"},
        expected_compute_units=1.0,
    )
    v0_store.save_experiment(experiment)

    contract = ExperimentContract(
        economic_hypothesis_id=economic_hypothesis.id,
        business_family="content",
        question="Does the price-anchor hook create external commercial intent?",
        intervention_dimensions={"hook": "price-anchor"},
        held_constant_dimensions=["topic"],
        expected_observation="At least one attributed external click inside 24 hours.",
        falsification_condition="No attributed click after the completed measurement window.",
        measurement=_measurement(),
    )

    store = PostgresExperimentContractStore(postgres_dsn)
    store.save_contract(contract)
    store.save_contract(contract)

    binding = ExperimentContractBinding(
        experiment_id=experiment.id,
        contract_id=contract.id,
    )
    store.bind_experiment(binding)
    store.bind_experiment(binding)

    assert store.get_contract(contract.id) == contract
    restored_binding = store.get_binding(experiment.id)
    assert restored_binding is not None
    assert restored_binding.experiment_id == experiment.id
    assert restored_binding.contract_id == contract.id

    changed_contract = contract.model_copy(update={"question": "A different question"})
    with pytest.raises(ValueError, match="immutable"):
        store.save_contract(changed_contract)

    replacement = ExperimentContract(
        economic_hypothesis_id=economic_hypothesis.id,
        business_family="content",
        question="Does a different hook create external commercial intent?",
        intervention_dimensions={"hook": "scarcity"},
        held_constant_dimensions=["topic"],
        expected_observation="At least one attributed external click inside 24 hours.",
        falsification_condition="No attributed click after the completed measurement window.",
        measurement=_measurement(),
        supersedes_contract_id=contract.id,
        contract_version=2,
    )
    store.save_contract(replacement)

    with pytest.raises(ValueError, match="rebound"):
        store.bind_experiment(
            ExperimentContractBinding(
                experiment_id=experiment.id,
                contract_id=replacement.id,
            )
        )


def test_child_contract_persists_lineage(postgres_dsn: str) -> None:
    legacy_hypothesis = Hypothesis(name="offer", thesis="Offer can convert", family="b2b")
    PostgresStore(postgres_dsn).save_hypothesis(legacy_hypothesis)
    economic_hypothesis = EconomicHypothesis.from_legacy(
        legacy_hypothesis,
        hypothesis_type=HypothesisType.OFFER,
    )
    PostgresBeliefStore(postgres_dsn).save_economic_hypothesis(economic_hypothesis)

    store = PostgresExperimentContractStore(postgres_dsn)
    parent = ExperimentContract(
        economic_hypothesis_id=economic_hypothesis.id,
        business_family="b2b",
        question="Does baseline outreach earn a qualified reply?",
        intervention_dimensions={"opening": "baseline"},
        expected_observation="At least one qualified reply.",
        falsification_condition="No qualified reply in the evidence window.",
        measurement=_measurement(),
    )
    store.save_contract(parent)

    child = ExperimentContract(
        economic_hypothesis_id=economic_hypothesis.id,
        business_family="b2b",
        question="Does a pain-first opening improve qualified replies?",
        intervention_dimensions={"opening": "pain-first"},
        held_constant_dimensions=["offer", "audience"],
        expected_observation="More qualified replies than the baseline cohort.",
        falsification_condition="No improvement after the evidence window.",
        measurement=_measurement(),
        parent_contract_id=parent.id,
    )
    store.save_contract(child)

    restored = store.get_contract(child.id)
    assert restored is not None
    assert restored.parent_contract_id == parent.id
