from __future__ import annotations

import os
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest

from business_master.domain.enums import (
    ComparisonOperator,
    EvidenceClass,
    EvidenceTier,
    HypothesisType,
    MetricAggregation,
)
from business_master.domain.experiment_contracts import (
    ExperimentContract,
    MeasurementContract,
    MetricCriterion,
)
from business_master.domain.family_evaluation import (
    BusinessFamily,
    EvaluationRecommendation,
    FamilyEvaluation,
    ReadinessStatus,
)
from business_master.domain.hypotheses import EconomicHypothesis
from business_master.domain.portfolio import (
    PortfolioCandidate,
    PortfolioPlanRequest,
    PortfolioRole,
    PortfolioValueEstimate,
)
from business_master.domain.resources import ResourceAvailability, ResourceVector
from business_master.policies.portfolio import PortfolioPolicy
from business_master.storage.beliefs_postgres import PostgresBeliefStore
from business_master.storage.experiment_contracts_postgres import PostgresExperimentContractStore
from business_master.storage.family_evaluations_postgres import PostgresFamilyEvaluationStore
from business_master.storage.portfolio_postgres import (
    PortfolioPlanConflictError,
    PostgresPortfolioStore,
)

NOW = datetime(2026, 10, 7, tzinfo=UTC)


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


def _seed_plan(dsn: str):
    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.HOOK,
        subject="portfolio persistence",
        proposition="A bounded candidate produces useful signal",
    )
    PostgresBeliefStore(dsn).save_economic_hypothesis(hypothesis)

    contract = ExperimentContract(
        economic_hypothesis_id=hypothesis.id,
        business_family="content",
        question="Does the candidate produce signal?",
        expected_observation="signal >= 1",
        falsification_condition="signal remains below threshold",
        measurement=MeasurementContract(
            window_seconds=3600,
            primary_metric="signal",
            supporting_criteria=[
                MetricCriterion(
                    metric="signal",
                    operator=ComparisonOperator.GTE,
                    threshold=1.0,
                    evidence_class=EvidenceClass.MARKET,
                    aggregation=MetricAggregation.SUM,
                )
            ],
        ),
        resource_requirements=ResourceVector(
            quantities={"gpu.local": Decimal("0.25")}
        ),
    )
    PostgresExperimentContractStore(dsn).save_contract(contract)

    evaluation = FamilyEvaluation(
        id=uuid4(),
        idempotency_key=f"family-eval-{hypothesis.id}",
        family=BusinessFamily.CONTENT,
        hypothesis_id=hypothesis.id,
        contract_id=contract.id,
        belief_state_version=1,
        current_tier=EvidenceTier.PROBE,
        policy_name="family_evaluation:content",
        policy_version="1",
        evidence_ids=[],
        interpretations=[],
        criteria=[],
        external_observations=1,
        independent_sources=1,
        replication_count=1,
        distinct_contexts=1,
        evidence_sufficient=True,
        supporting_signal=True,
        falsified=False,
        economic_readiness=ReadinessStatus.UNKNOWN,
        operational_readiness=ReadinessStatus.READY,
        recommendation=EvaluationRecommendation.REPLICATE,
        rationale="persisted upstream evaluation",
        evaluated_at=NOW,
    )
    PostgresFamilyEvaluationStore(dsn).save(evaluation)

    candidate = PortfolioCandidate(
        family_evaluation=evaluation,
        contract=contract,
        roles=(PortfolioRole.SIGNAL,),
        value=PortfolioValueEstimate(information_value=0.9, feedback_speed=0.8),
        group_key="content-hooks",
    )
    availability = ResourceAvailability(
        capacity=ResourceVector(quantities={"gpu.local": Decimal("1")}),
        reserved=ResourceVector(),
        available=ResourceVector(quantities={"gpu.local": Decimal("1")}),
    )
    plan = PortfolioPolicy().plan(
        PortfolioPlanRequest(
            idempotency_key="portfolio:persist:1",
            candidates=(candidate,),
            availability=availability,
            base_currency="USD",
            created_at=NOW,
        )
    )
    return plan


def test_portfolio_plan_is_durable_and_retry_idempotent(postgres_dsn: str) -> None:
    plan = _seed_plan(postgres_dsn)
    store = PostgresPortfolioStore(postgres_dsn)

    first = store.save(plan)
    retry = store.save(plan)
    loaded = store.get_by_idempotency_key(plan.idempotency_key)

    assert retry == first
    assert loaded == plan
    assert loaded is not None
    assert loaded.base_currency == "USD"
    assert len(plan.allocations) == 1

    with psycopg.connect(postgres_dsn) as conn:
        experiment_count = conn.execute("SELECT COUNT(*) FROM experiment").fetchone()
        reservation_count = conn.execute(
            "SELECT COUNT(*) FROM resource_reservation"
        ).fetchone()

    assert experiment_count == (0,)
    assert reservation_count == (0,)


def test_portfolio_idempotency_key_rejects_semantic_reuse(postgres_dsn: str) -> None:
    plan = _seed_plan(postgres_dsn)
    store = PostgresPortfolioStore(postgres_dsn)
    store.save(plan)

    conflicting = plan.model_copy(update={"policy_version": "different"})
    with pytest.raises(PortfolioPlanConflictError, match="different semantics"):
        store.save(conflicting)


def test_portfolio_store_requires_persisted_family_evaluation(postgres_dsn: str) -> None:
    plan = _seed_plan(postgres_dsn)
    evaluation_id = plan.allocations[0].family_evaluation_id
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("DELETE FROM family_evaluation WHERE id = %s", (evaluation_id,))

    with pytest.raises(ValueError, match="family evaluation does not exist"):
        PostgresPortfolioStore(postgres_dsn).save(plan)


def test_portfolio_store_rejects_tampered_lineage(postgres_dsn: str) -> None:
    plan = _seed_plan(postgres_dsn)
    allocation = plan.allocations[0].model_copy(update={"hypothesis_id": uuid4()})
    tampered = plan.model_copy(update={"allocations": [allocation]})

    with pytest.raises(ValueError, match="hypothesis lineage"):
        PostgresPortfolioStore(postgres_dsn).save(tampered)
