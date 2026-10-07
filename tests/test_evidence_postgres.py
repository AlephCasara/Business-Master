from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest

from business_master.controllers.experiments import ExperimentController
from business_master.domain.enums import (
    ComparisonOperator,
    EvidenceClass,
    EvidenceProvenance,
    EvidenceTargetKind,
    HypothesisType,
    MetricAggregation,
)
from business_master.domain.evidence import EvidenceAssociation, EvidenceRecord
from business_master.domain.experiment_contracts import (
    ExperimentContract,
    MeasurementContract,
    MetricCriterion,
)
from business_master.domain.experiments import Experiment
from business_master.domain.hypotheses import EconomicHypothesis, Hypothesis
from business_master.storage.beliefs_postgres import PostgresBeliefStore
from business_master.storage.evidence_postgres import PostgresEvidenceStore
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


def _persist_targets(
    postgres_dsn: str,
) -> tuple[EconomicHypothesis, ExperimentContract, Experiment]:
    legacy = Hypothesis(
        name="chart-hook",
        thesis="A chart hook can create commercial intent",
        family="content",
        market="US",
    )
    legacy_store = PostgresStore(postgres_dsn)
    legacy_store.save_hypothesis(legacy)

    economic = EconomicHypothesis.from_legacy(
        legacy,
        hypothesis_type=HypothesisType.HOOK,
        mechanism="Use a concrete chart hook to earn an external click.",
    )
    PostgresBeliefStore(postgres_dsn).save_economic_hypothesis(economic)

    experiment = ExperimentController().create_probe(
        legacy,
        dimensions={"hook": "price-anchor"},
        expected_compute_units=1.0,
    )
    legacy_store.save_experiment(experiment)

    contract = ExperimentContract(
        economic_hypothesis_id=economic.id,
        business_family="content",
        question="Does the chart hook create external commercial intent?",
        intervention_dimensions={"hook": "price-anchor"},
        expected_observation="At least one attributed external click.",
        falsification_condition="No click after the completed evidence window.",
        measurement=_measurement(),
    )
    PostgresExperimentContractStore(postgres_dsn).save_contract(contract)
    return economic, contract, experiment


def test_evidence_roundtrip_association_lineage_and_immutability(postgres_dsn: str) -> None:
    economic, contract, experiment = _persist_targets(postgres_dsn)
    store = PostgresEvidenceStore(postgres_dsn)

    observed = EvidenceRecord(
        evidence_class=EvidenceClass.MARKET,
        provenance=EvidenceProvenance.OBSERVED_OFFICIAL_EXTERNAL,
        kind="metric_snapshot",
        source="youtube.analytics",
        independence_key="channel:finance-01",
        source_event_id="video-123:2026-10-07T00:00:00Z",
        subject_type="experiment",
        subject_id=experiment.id,
        features={"views": 1200, "external_clicks": 3},
        payload_ref="r2://evidence/video-123.json",
    )
    store.save_record(observed)
    store.save_record(observed)

    associations = [
        EvidenceAssociation(
            evidence_id=observed.id,
            target_kind=EvidenceTargetKind.ECONOMIC_HYPOTHESIS,
            target_id=economic.id,
        ),
        EvidenceAssociation(
            evidence_id=observed.id,
            target_kind=EvidenceTargetKind.EXPERIMENT_CONTRACT,
            target_id=contract.id,
        ),
        EvidenceAssociation(
            evidence_id=observed.id,
            target_kind=EvidenceTargetKind.EXPERIMENT,
            target_id=experiment.id,
        ),
    ]
    for association in associations:
        store.bind_record(association)
        store.bind_record(association)

    assert store.get_record(observed.id) == observed
    assert store.list_records_for_target(
        EvidenceTargetKind.EXPERIMENT_CONTRACT,
        contract.id,
        evidence_class=EvidenceClass.MARKET,
    ) == [observed]

    calculated = EvidenceRecord(
        evidence_class=EvidenceClass.ECONOMIC,
        provenance=EvidenceProvenance.CALCULATED,
        kind="attributed_contribution",
        source="business_master.unit_economics",
        subject_type="experiment",
        subject_id=experiment.id,
        features={"contribution": 8.75},
        input_evidence_ids=[observed.id],
    )
    store.save_record(calculated)
    assert store.get_record(calculated.id) == calculated

    changed = observed.model_copy(update={"features": {"views": 9999}})
    with pytest.raises(ValueError, match="immutable"):
        store.save_record(changed)


def test_evidence_rejects_duplicate_source_event_and_missing_lineage(postgres_dsn: str) -> None:
    _, _, experiment = _persist_targets(postgres_dsn)
    store = PostgresEvidenceStore(postgres_dsn)

    observed = EvidenceRecord(
        evidence_class=EvidenceClass.TECHNICAL,
        provenance=EvidenceProvenance.OBSERVED_OWN,
        kind="publish_accepted",
        source="youtube.publisher",
        source_event_id="request-abc",
        subject_type="experiment",
        subject_id=experiment.id,
        features={"accepted": True},
    )
    store.save_record(observed)

    duplicate = observed.model_copy(update={"id": uuid4()})
    with pytest.raises(ValueError, match="source event"):
        store.save_record(duplicate)

    missing_parent = EvidenceRecord(
        evidence_class=EvidenceClass.ECONOMIC,
        provenance=EvidenceProvenance.INFERRED,
        kind="estimated_ltv",
        source="business_master.model",
        input_evidence_ids=[uuid4()],
    )
    with pytest.raises(ValueError, match="input evidence does not exist"):
        store.save_record(missing_parent)


def test_evidence_binding_rejects_dangling_target(postgres_dsn: str) -> None:
    store = PostgresEvidenceStore(postgres_dsn)
    record = EvidenceRecord(
        evidence_class=EvidenceClass.MARKET,
        provenance=EvidenceProvenance.OBSERVED_PUBLIC,
        kind="public_demand_signal",
        source="public_search",
        features={"mentions": 12},
    )
    store.save_record(record)

    with pytest.raises(ValueError, match="target does not exist"):
        store.bind_record(
            EvidenceAssociation(
                evidence_id=record.id,
                target_kind=EvidenceTargetKind.ECONOMIC_HYPOTHESIS,
                target_id=uuid4(),
            )
        )
