from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

import psycopg
import pytest

from business_master.domain.belief_updates import BeliefUpdateRequest
from business_master.domain.beliefs import BeliefState
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
from business_master.domain.family_evaluation import (
    EvaluationRecommendation,
    FamilyEvaluationContext,
    FamilyEvaluationRequest,
)
from business_master.domain.hypotheses import EconomicHypothesis
from business_master.policies.family_evaluation import policy_for_family
from business_master.storage.belief_updates_postgres import PostgresBeliefUpdateEngine
from business_master.storage.beliefs_postgres import PostgresBeliefStore
from business_master.storage.evidence_postgres import PostgresEvidenceStore
from business_master.storage.experiment_contracts_postgres import PostgresExperimentContractStore
from business_master.storage.family_evaluations_postgres import (
    FamilyEvaluationConflictError,
    PostgresFamilyEvaluationStore,
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


def _setup(postgres_dsn: str) -> tuple[EconomicHypothesis, ExperimentContract, EvidenceRecord]:
    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.HOOK,
        subject="content hook",
        proposition="The hook creates external commercial intent",
    )
    PostgresBeliefStore(postgres_dsn).save_economic_hypothesis(hypothesis)

    contract = ExperimentContract(
        economic_hypothesis_id=hypothesis.id,
        business_family="content",
        question="Does the hook produce an attributed external click?",
        expected_observation="At least one attributed click.",
        falsification_condition="No attributed click after the measurement window.",
        measurement=MeasurementContract(
            window_seconds=3600,
            primary_metric="external_clicks",
            minimum_external_observations=1,
            supporting_criteria=[
                MetricCriterion(
                    metric="external_clicks",
                    operator=ComparisonOperator.GTE,
                    threshold=1.0,
                    evidence_class=EvidenceClass.MARKET,
                    aggregation=MetricAggregation.SUM,
                )
            ],
            falsifying_criteria=[
                MetricCriterion(
                    metric="external_clicks",
                    operator=ComparisonOperator.LTE,
                    threshold=0.0,
                    evidence_class=EvidenceClass.MARKET,
                    aggregation=MetricAggregation.SUM,
                )
            ],
        ),
    )
    PostgresExperimentContractStore(postgres_dsn).save_contract(contract)

    evidence = EvidenceRecord(
        evidence_class=EvidenceClass.MARKET,
        provenance=EvidenceProvenance.OBSERVED_OWN,
        kind="attributed_click",
        source="youtube",
        source_event_id="click-1",
        observed_at=NOW,
        features={"external_clicks": 1.0},
    )
    evidence_store = PostgresEvidenceStore(postgres_dsn)
    evidence_store.save_record(evidence)
    evidence_store.bind_record(
        EvidenceAssociation(
            evidence_id=evidence.id,
            target_kind=EvidenceTargetKind.ECONOMIC_HYPOTHESIS,
            target_id=hypothesis.id,
        )
    )
    return hypothesis, contract, evidence


def test_family_evaluation_is_append_only_and_feeds_pr7(postgres_dsn: str) -> None:
    hypothesis, contract, evidence = _setup(postgres_dsn)
    belief = BeliefState(hypothesis_id=hypothesis.id)
    request = FamilyEvaluationRequest(
        idempotency_key="content-eval-1",
        hypothesis=hypothesis,
        contract=contract,
        belief_state=belief,
        evidence=(evidence,),
        context=FamilyEvaluationContext(replication_count=1),
        evaluated_at=NOW,
    )
    evaluation = policy_for_family("content").evaluate(request)
    assert evaluation.recommendation is EvaluationRecommendation.GRADUATE

    store = PostgresFamilyEvaluationStore(postgres_dsn)
    persisted = store.save(evaluation)
    retry = store.save(evaluation)
    assert retry == persisted
    assert store.get(evaluation.id) == evaluation
    assert list(store.list_for_hypothesis(hypothesis.id)) == [evaluation]

    changed = evaluation.model_copy(update={"rationale": "different semantics"})
    with pytest.raises(FamilyEvaluationConflictError, match="different semantics"):
        store.save(changed)

    directive = evaluation.interpretations[0]
    update = PostgresBeliefUpdateEngine(postgres_dsn).apply(
        BeliefUpdateRequest(
            hypothesis_id=hypothesis.id,
            evidence_id=directive.evidence_id,
            interpretation=directive.interpretation,
            strength=directive.strength,
            rationale=directive.rationale,
            evaluated_at=NOW,
        )
    )

    assert update.update.applied is True
    assert update.state.state_version == 2
    assert update.state.confidence > 0


def test_family_evaluation_does_not_mutate_belief_by_itself(postgres_dsn: str) -> None:
    hypothesis, contract, evidence = _setup(postgres_dsn)
    request = FamilyEvaluationRequest(
        idempotency_key="content-eval-no-mutation",
        hypothesis=hypothesis,
        contract=contract,
        belief_state=BeliefState(hypothesis_id=hypothesis.id),
        evidence=(evidence,),
        context=FamilyEvaluationContext(replication_count=1),
        evaluated_at=NOW,
    )

    evaluation = policy_for_family("content").evaluate(request)
    PostgresFamilyEvaluationStore(postgres_dsn).save(evaluation)

    assert PostgresBeliefStore(postgres_dsn).get_belief_state(hypothesis.id) is None
