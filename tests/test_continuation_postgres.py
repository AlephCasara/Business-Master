from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import psycopg
import pytest
from psycopg.types.json import Jsonb

from business_master.controllers.experiments import ExperimentController
from business_master.domain.beliefs import BeliefState
from business_master.domain.capital import CapitalRequirement, SpendCategory
from business_master.domain.decisions import AutonomousContinuationRequest, ContinuationKind
from business_master.domain.enums import (
    ComparisonOperator,
    EvidenceClass,
    EvidenceTier,
    ExperimentStatus,
    HypothesisType,
    MetricAggregation,
    ResourceKind,
    RiskLevel,
)
from business_master.domain.experiment_contracts import (
    ExperimentContract,
    ExperimentContractBinding,
    MeasurementContract,
    MetricCriterion,
)
from business_master.domain.experiments import Experiment
from business_master.domain.family_evaluation import (
    BusinessFamily,
    EvaluationRecommendation,
    FamilyEvaluation,
    ReadinessStatus,
)
from business_master.domain.hypotheses import EconomicHypothesis, Hypothesis
from business_master.domain.portfolio import (
    PortfolioAllocation,
    PortfolioCandidate,
    PortfolioPlanRequest,
    PortfolioRole,
    PortfolioValueEstimate,
    RiskAssessment,
)
from business_master.domain.resources import Resource, ResourceAvailability, ResourceVector
from business_master.policies.continuation import (
    CapitalAuthorizationRequiredError,
    HumanGateRequiredError,
)
from business_master.policies.portfolio import PortfolioPolicy
from business_master.storage.beliefs_postgres import PostgresBeliefStore
from business_master.storage.continuation_postgres import (
    ContinuationConflictError,
    ContinuationLineageError,
    PostgresContinuationStore,
    StaleContinuationError,
)
from business_master.storage.experiment_contracts_postgres import PostgresExperimentContractStore
from business_master.storage.family_evaluations_postgres import PostgresFamilyEvaluationStore
from business_master.storage.portfolio_postgres import PostgresPortfolioStore
from business_master.storage.postgres import PostgresStore
from business_master.storage.resource_reservations_postgres import ResourceCapacityError

NOW = datetime(2026, 10, 7, 10, tzinfo=UTC)


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


@dataclass(frozen=True, slots=True)
class SeededCase:
    legacy_hypothesis: Hypothesis
    economic_hypothesis: EconomicHypothesis
    parent: Experiment
    contract: ExperimentContract
    evaluation: FamilyEvaluation
    allocation: PortfolioAllocation


def _measurement() -> MeasurementContract:
    return MeasurementContract(
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
    )


def _persist_belief_version(dsn: str, belief: BeliefState) -> None:
    with psycopg.connect(dsn) as conn:
        conn.execute(
            """
            INSERT INTO belief_state_version (
                hypothesis_id, state_version, confidence, uncertainty, evidence_count,
                valid_from, last_evidence_at, freshness, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                belief.hypothesis_id,
                belief.state_version,
                belief.confidence,
                belief.uncertainty,
                belief.evidence_count,
                belief.valid_from,
                belief.last_evidence_at,
                belief.freshness,
                belief.updated_at,
            ),
        )


def _seed_case(
    dsn: str,
    *,
    recommendation: EvaluationRecommendation = EvaluationRecommendation.REPLICATE,
    tier: EvidenceTier = EvidenceTier.PROBE,
    resource_name: str = "gpu.local",
    demand: Decimal = Decimal("1"),
    actual_capacity: Decimal = Decimal("1"),
    plan_capacity: Decimal | None = None,
    risk: RiskAssessment | None = None,
    capital: CapitalRequirement | None = None,
    key_prefix: str | None = None,
) -> SeededCase:
    prefix = key_prefix or uuid4().hex
    legacy = Hypothesis(
        name=f"continuation-{prefix}",
        thesis="A bounded continuation can acquire more decision-relevant evidence.",
        family="content",
        tier=tier,
    )
    v0_store = PostgresStore(dsn)
    v0_store.save_hypothesis(legacy)

    economic = EconomicHypothesis.from_legacy(
        legacy,
        hypothesis_type=HypothesisType.HOOK,
        mechanism="Repeat the bounded intervention against the same measurement contract.",
    )
    belief_store = PostgresBeliefStore(dsn)
    belief_store.save_economic_hypothesis(economic)
    belief = BeliefState(
        hypothesis_id=economic.id,
        confidence=0.6,
        uncertainty=0.4,
        evidence_count=1,
        valid_from=NOW,
        last_evidence_at=NOW,
        freshness=1.0,
        state_version=1,
        updated_at=NOW,
    )
    belief_store.save_belief_state(belief)
    _persist_belief_version(dsn, belief)

    parent = ExperimentController().create_probe(
        legacy,
        dimensions={"hook": "baseline", "topic": "consumer-finance"},
    ).model_copy(
        update={
            "status": ExperimentStatus.COMPLETE,
            "tier": tier,
            "completed_at": NOW,
        }
    )
    v0_store.save_experiment(parent)

    requirements = (
        ResourceVector()
        if demand == 0
        else ResourceVector(quantities={resource_name: demand})
    )
    contract = ExperimentContract(
        economic_hypothesis_id=economic.id,
        business_family="content",
        question="Does the bounded continuation produce another external signal?",
        intervention_dimensions={"hook": "baseline"},
        held_constant_dimensions=["topic"],
        expected_observation="At least one external signal in the measurement window.",
        falsification_condition="No external signal after the complete window.",
        measurement=_measurement(),
        resource_requirements=requirements,
    )
    contract_store = PostgresExperimentContractStore(dsn)
    contract_store.save_contract(contract)
    contract_store.bind_experiment(
        ExperimentContractBinding(
            experiment_id=parent.id,
            contract_id=contract.id,
            bound_at=NOW,
        )
    )

    evaluation = FamilyEvaluation(
        id=uuid4(),
        idempotency_key=f"family:{prefix}:1",
        family=BusinessFamily.CONTENT,
        hypothesis_id=economic.id,
        contract_id=contract.id,
        belief_state_version=1,
        current_tier=tier,
        policy_name="family_evaluation:content",
        policy_version="2",
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
        recommendation=recommendation,
        rationale="Persisted family evaluation selected a bounded continuation.",
        evaluated_at=NOW,
    )
    PostgresFamilyEvaluationStore(dsn).save(evaluation)

    if demand != 0:
        v0_store.save_resource(
            Resource(
                name=resource_name,
                kind=ResourceKind.GPU,
                capacity=actual_capacity,
                last_seen_at=NOW,
            )
        )
    capacity = actual_capacity if plan_capacity is None else plan_capacity
    availability = (
        ResourceAvailability(
            capacity=ResourceVector(),
            reserved=ResourceVector(),
            available=ResourceVector(),
        )
        if demand == 0
        else ResourceAvailability(
            capacity=ResourceVector(quantities={resource_name: capacity}),
            reserved=ResourceVector(),
            available=ResourceVector(quantities={resource_name: capacity}),
        )
    )
    candidate = PortfolioCandidate(
        family_evaluation=evaluation,
        contract=contract,
        roles=(PortfolioRole.SIGNAL,),
        value=PortfolioValueEstimate(
            information_value=0.9,
            feedback_speed=0.8,
            uncertainty=0.4,
        ),
        risk=risk or RiskAssessment(level=RiskLevel.LOW),
        capital_requirement=capital,
        group_key=f"content-{prefix}",
    )
    plan = PortfolioPolicy().plan(
        PortfolioPlanRequest(
            idempotency_key=f"portfolio:{prefix}:1",
            candidates=(candidate,),
            availability=availability,
            base_currency="USD",
            allow_human_gate=(risk is not None and risk.human_gate_required),
            created_at=NOW,
        )
    )
    assert len(plan.allocations) == 1
    PostgresPortfolioStore(dsn).save(plan)
    return SeededCase(
        legacy_hypothesis=legacy,
        economic_hypothesis=economic,
        parent=parent,
        contract=contract,
        evaluation=evaluation,
        allocation=plan.allocations[0],
    )


def _request(case: SeededCase, key: str) -> AutonomousContinuationRequest:
    return AutonomousContinuationRequest(
        idempotency_key=key,
        parent_experiment_id=case.parent.id,
        portfolio_allocation_id=case.allocation.id,
        reservation_expires_at=NOW + timedelta(hours=1),
    )


def _insert_active_capital_authorization(dsn: str, case: SeededCase) -> UUID:
    requirement = case.allocation.capital_requirement
    assert requirement is not None
    authorization_id = uuid4()
    with psycopg.connect(dsn) as conn:
        conn.execute(
            """
            INSERT INTO capital_authorization (
                id, idempotency_key, portfolio_allocation_id, family_evaluation_id,
                hypothesis_id, amount, currency, category, stage, risk, blast_radius,
                reversible, human_gate_required, policy_name, policy_version, envelope,
                ledger_cash_at_authorization, active_outstanding_before,
                period_committed_before, status, rationale, requested_at, authorized_at,
                expires_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                authorization_id,
                f"capital:{case.allocation.id}",
                case.allocation.id,
                case.allocation.family_evaluation_id,
                case.allocation.hypothesis_id,
                requirement.amount,
                requirement.currency,
                requirement.category.value,
                "probe",
                case.allocation.risk.level.value,
                case.allocation.risk.blast_radius,
                case.allocation.risk.reversible,
                case.allocation.risk.human_gate_required,
                "capital-test",
                "1",
                Jsonb({}),
                Decimal("100"),
                Decimal("0"),
                Decimal("0"),
                "active",
                "Test authorization for PR10 continuation.",
                NOW,
                NOW,
                NOW + timedelta(hours=1),
            ),
        )
    return authorization_id


def test_replication_is_atomic_durable_and_restart_idempotent(postgres_dsn: str) -> None:
    case = _seed_case(postgres_dsn, key_prefix="replicate-roundtrip")
    request = _request(case, "continuation:replicate:roundtrip")

    first = PostgresContinuationStore(postgres_dsn, clock=lambda: NOW).continue_from(request)
    restarted = PostgresContinuationStore(postgres_dsn, clock=lambda: NOW).continue_from(request)
    loaded = PostgresContinuationStore(postgres_dsn).get_by_idempotency_key(
        request.idempotency_key
    )

    assert restarted == first
    assert loaded == first
    assert first.decision.continuation_kind is ContinuationKind.REPLICATE
    assert first.child_experiment is not None
    assert first.child_contract is not None
    assert first.resource_reservation is not None
    assert first.child_experiment.parent_id == case.parent.id
    assert first.child_experiment.tier is EvidenceTier.PROBE
    assert first.child_experiment.dimensions == case.parent.dimensions
    assert first.child_contract.parent_contract_id == case.contract.id
    assert first.child_contract.supersedes_contract_id is None
    assert first.child_contract.origin_decision_id == first.decision.id
    assert first.child_contract.resource_requirements == case.contract.resource_requirements
    assert first.child_contract.measurement == case.contract.measurement
    assert first.resource_reservation.owner_id == first.child_experiment.id
    assert first.resource_reservation.requirements == case.contract.resource_requirements
    assert first.decision.family_evaluation_id == case.evaluation.id
    assert first.decision.belief_state_version == 1
    assert first.decision.source_contract_id == case.contract.id

    with psycopg.connect(postgres_dsn) as conn:
        decision_count = conn.execute(
            "SELECT COUNT(*) FROM decision WHERE idempotency_key = %s",
            (request.idempotency_key,),
        ).fetchone()
        child_count = conn.execute(
            "SELECT COUNT(*) FROM experiment WHERE parent_id = %s",
            (case.parent.id,),
        ).fetchone()
        reservation_count = conn.execute(
            "SELECT COUNT(*) FROM resource_reservation WHERE owner_id = %s",
            (first.child_experiment.id,),
        ).fetchone()

    assert decision_count == (1,)
    assert child_count == (1,)
    assert reservation_count == (1,)


@pytest.mark.parametrize(
    ("current_tier", "expected_tier"),
    [
        (EvidenceTier.PROBE, EvidenceTier.PILOT),
        (EvidenceTier.PILOT, EvidenceTier.SCALE),
    ],
)
def test_graduation_advances_exactly_one_tier_without_resource_inflation(
    postgres_dsn: str,
    current_tier: EvidenceTier,
    expected_tier: EvidenceTier,
) -> None:
    case = _seed_case(
        postgres_dsn,
        recommendation=EvaluationRecommendation.GRADUATE,
        tier=current_tier,
        demand=Decimal("0.5"),
        key_prefix=f"graduate-{current_tier.value}",
    )

    result = PostgresContinuationStore(postgres_dsn, clock=lambda: NOW).continue_from(
        _request(case, f"continuation:graduate:{current_tier.value}")
    )

    assert result.child_experiment is not None
    assert result.child_contract is not None
    assert result.decision.continuation_kind is ContinuationKind.GRADUATE
    assert result.decision.target_tier is expected_tier
    assert result.child_experiment.tier is expected_tier
    assert result.child_contract.parent_contract_id == case.contract.id
    assert result.child_contract.supersedes_contract_id == case.contract.id
    assert result.child_contract.resource_requirements == case.contract.resource_requirements
    assert result.child_contract.budget == case.contract.budget


def test_empty_child_resource_demand_creates_no_reservation(postgres_dsn: str) -> None:
    case = _seed_case(
        postgres_dsn,
        recommendation=EvaluationRecommendation.REPLICATE,
        demand=Decimal("0"),
        key_prefix="empty-resource-demand",
    )

    result = PostgresContinuationStore(postgres_dsn, clock=lambda: NOW).continue_from(
        _request(case, "continuation:empty-resource-demand")
    )

    assert result.child_experiment is not None
    assert result.resource_reservation is None
    assert result.decision.resource_reservation_id is None
    with psycopg.connect(postgres_dsn) as conn:
        count = conn.execute("SELECT COUNT(*) FROM resource_reservation").fetchone()
    assert count == (0,)


def test_continue_persists_decision_without_manufacturing_child(postgres_dsn: str) -> None:
    case = _seed_case(
        postgres_dsn,
        recommendation=EvaluationRecommendation.CONTINUE,
        demand=Decimal("0"),
        key_prefix="continue-no-child",
    )

    result = PostgresContinuationStore(postgres_dsn, clock=lambda: NOW).continue_from(
        _request(case, "continuation:continue:no-child")
    )

    assert result.decision.continuation_kind is ContinuationKind.NONE
    assert result.child_experiment is None
    assert result.child_contract is None
    assert result.resource_reservation is None
    with psycopg.connect(postgres_dsn) as conn:
        children = conn.execute(
            "SELECT COUNT(*) FROM experiment WHERE parent_id = %s",
            (case.parent.id,),
        ).fetchone()
    assert children == (0,)


def test_stale_family_evaluation_is_rejected_before_decision(postgres_dsn: str) -> None:
    case = _seed_case(postgres_dsn, key_prefix="stale-evaluation")
    newer = case.evaluation.model_copy(
        update={
            "id": uuid4(),
            "idempotency_key": "family:stale-evaluation:2",
            "evaluated_at": NOW + timedelta(minutes=1),
        }
    )
    PostgresFamilyEvaluationStore(postgres_dsn).save(newer)

    with pytest.raises(StaleContinuationError, match="latest family evaluation"):
        PostgresContinuationStore(postgres_dsn, clock=lambda: NOW).continue_from(
            _request(case, "continuation:stale-evaluation")
        )

    with psycopg.connect(postgres_dsn) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM decision WHERE portfolio_allocation_id = %s",
            (case.allocation.id,),
        ).fetchone()
    assert count == (0,)


def test_stale_belief_version_is_rejected_before_decision(postgres_dsn: str) -> None:
    case = _seed_case(postgres_dsn, key_prefix="stale-belief")
    newer = BeliefState(
        hypothesis_id=case.economic_hypothesis.id,
        confidence=0.7,
        uncertainty=0.3,
        evidence_count=2,
        valid_from=NOW + timedelta(minutes=1),
        last_evidence_at=NOW + timedelta(minutes=1),
        freshness=1.0,
        state_version=2,
        updated_at=NOW + timedelta(minutes=1),
    )
    PostgresBeliefStore(postgres_dsn).save_belief_state(newer)
    _persist_belief_version(postgres_dsn, newer)

    with pytest.raises(StaleContinuationError, match="latest belief-state version"):
        PostgresContinuationStore(postgres_dsn, clock=lambda: NOW).continue_from(
            _request(case, "continuation:stale-belief")
        )


def test_parent_contract_binding_drift_is_rejected(postgres_dsn: str) -> None:
    case = _seed_case(postgres_dsn, key_prefix="binding-drift")
    sibling = case.contract.model_copy(
        update={
            "id": uuid4(),
            "question": "A sibling contract used only to prove binding drift rejection.",
            "contract_version": 2,
        }
    )
    PostgresExperimentContractStore(postgres_dsn).save_contract(sibling)
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute(
            "UPDATE experiment_contract_binding SET contract_id = %s WHERE experiment_id = %s",
            (sibling.id, case.parent.id),
        )

    with pytest.raises(ContinuationLineageError, match="different source contract"):
        PostgresContinuationStore(postgres_dsn, clock=lambda: NOW).continue_from(
            _request(case, "continuation:binding-drift")
        )


def test_human_gate_blocks_autonomous_child_without_partial_state(postgres_dsn: str) -> None:
    case = _seed_case(
        postgres_dsn,
        risk=RiskAssessment(
            level=RiskLevel.MEDIUM,
            blast_radius=0.3,
            reversible=True,
            human_gate_required=True,
        ),
        key_prefix="human-gate",
    )

    with pytest.raises(HumanGateRequiredError, match="human gate"):
        PostgresContinuationStore(postgres_dsn, clock=lambda: NOW).continue_from(
            _request(case, "continuation:human-gate")
        )

    with psycopg.connect(postgres_dsn) as conn:
        decisions = conn.execute(
            "SELECT COUNT(*) FROM decision WHERE portfolio_allocation_id = %s",
            (case.allocation.id,),
        ).fetchone()
    assert decisions == (0,)


def test_capital_gate_requires_active_matching_authorization_and_does_not_consume_it(
    postgres_dsn: str,
) -> None:
    requirement = CapitalRequirement(
        amount=Decimal("25"),
        currency="USD",
        category=SpendCategory.PAID_ADS,
    )
    case = _seed_case(
        postgres_dsn,
        capital=requirement,
        key_prefix="capital-gate",
    )
    request = _request(case, "continuation:capital-gate")
    store = PostgresContinuationStore(postgres_dsn, clock=lambda: NOW)

    with pytest.raises(CapitalAuthorizationRequiredError, match="active PR9"):
        store.continue_from(request)

    authorization_id = _insert_active_capital_authorization(postgres_dsn, case)
    result = store.continue_from(request)

    assert result.decision.capital_authorization_id == authorization_id
    with psycopg.connect(postgres_dsn) as conn:
        row = conn.execute(
            "SELECT status, consumed_at, ledger_transaction_id "
            "FROM capital_authorization WHERE id = %s",
            (authorization_id,),
        ).fetchone()
    assert row == ("active", None, None)


def test_conflicting_idempotency_and_second_decision_from_same_allocation_are_rejected(
    postgres_dsn: str,
) -> None:
    case = _seed_case(postgres_dsn, key_prefix="decision-conflicts")
    store = PostgresContinuationStore(postgres_dsn, clock=lambda: NOW)
    request = _request(case, "continuation:decision-conflicts")
    first = store.continue_from(request)
    assert first.child_experiment is not None

    conflicting = request.model_copy(update={"parent_experiment_id": uuid4()})
    with pytest.raises(ContinuationConflictError, match="different semantics"):
        store.continue_from(conflicting)

    second_key = request.model_copy(update={"idempotency_key": "continuation:decision-conflicts:2"})
    with pytest.raises(ContinuationConflictError, match="already produced"):
        store.continue_from(second_key)


def test_resource_capacity_failure_rolls_back_decision_contract_and_child(
    postgres_dsn: str,
) -> None:
    case = _seed_case(
        postgres_dsn,
        demand=Decimal("2"),
        actual_capacity=Decimal("1"),
        plan_capacity=Decimal("2"),
        key_prefix="capacity-rollback",
    )
    request = _request(case, "continuation:capacity-rollback")

    with pytest.raises(ResourceCapacityError, match="insufficient capacity"):
        PostgresContinuationStore(postgres_dsn, clock=lambda: NOW).continue_from(request)

    with psycopg.connect(postgres_dsn) as conn:
        decision_count = conn.execute(
            "SELECT COUNT(*) FROM decision WHERE idempotency_key = %s",
            (request.idempotency_key,),
        ).fetchone()
        child_count = conn.execute(
            "SELECT COUNT(*) FROM experiment WHERE parent_id = %s",
            (case.parent.id,),
        ).fetchone()
        child_contract_count = conn.execute(
            "SELECT COUNT(*) FROM experiment_contract WHERE parent_contract_id = %s",
            (case.contract.id,),
        ).fetchone()
        reservation_count = conn.execute(
            "SELECT COUNT(*) FROM resource_reservation WHERE owner_type = 'experiment'"
        ).fetchone()

    assert decision_count == (0,)
    assert child_count == (0,)
    assert child_contract_count == (0,)
    assert reservation_count == (0,)


def test_concurrent_continuations_cannot_overallocate_same_resource(postgres_dsn: str) -> None:
    first_case = _seed_case(
        postgres_dsn,
        resource_name="gpu.shared",
        demand=Decimal("1"),
        actual_capacity=Decimal("1"),
        key_prefix="concurrency-a",
    )
    second_case = _seed_case(
        postgres_dsn,
        resource_name="gpu.shared",
        demand=Decimal("1"),
        actual_capacity=Decimal("1"),
        key_prefix="concurrency-b",
    )
    first_request = _request(first_case, "continuation:concurrency:a")
    second_request = _request(second_case, "continuation:concurrency:b")

    def run(request: AutonomousContinuationRequest):
        try:
            return PostgresContinuationStore(postgres_dsn, clock=lambda: NOW).continue_from(request)
        except (ResourceCapacityError, psycopg.errors.SerializationFailure) as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(run, (first_request, second_request)))

    successes = [item for item in results if not isinstance(item, Exception)]
    failures = [item for item in results if isinstance(item, Exception)]
    assert len(successes) == 1
    assert len(failures) == 1

    with psycopg.connect(postgres_dsn) as conn:
        reserved = conn.execute(
            """
            SELECT COALESCE(SUM(item.amount), 0)
            FROM resource_reservation_item AS item
            JOIN resource_reservation AS reservation ON reservation.id = item.reservation_id
            JOIN resource ON resource.id = item.resource_id
            WHERE resource.name = 'gpu.shared' AND reservation.status = 'active'
            """
        ).fetchone()
        decision_count = conn.execute(
            """
            SELECT COUNT(*) FROM decision
            WHERE idempotency_key IN (%s, %s)
            """,
            (first_request.idempotency_key, second_request.idempotency_key),
        ).fetchone()

    assert reserved == (Decimal("1.000000"),)
    assert decision_count == (1,)
