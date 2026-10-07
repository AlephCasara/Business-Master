from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from threading import Barrier
from uuid import uuid4

import psycopg
import pytest

from business_master.domain.capital import (
    CapitalAuthorizationRequest,
    CapitalAuthorizationStatus,
    CapitalEnvelope,
    CapitalRequirement,
    CapitalStage,
    SpendCategory,
)
from business_master.domain.enums import (
    ComparisonOperator,
    EvidenceClass,
    EvidenceTier,
    HypothesisType,
    MetricAggregation,
    RiskLevel,
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
from business_master.domain.ledger import (
    LedgerAccount,
    LedgerPosting,
    LedgerSide,
    LedgerTransactionRequest,
)
from business_master.domain.portfolio import (
    PortfolioCandidate,
    PortfolioPlanRequest,
    PortfolioRole,
    PortfolioValueEstimate,
)
from business_master.domain.resources import ResourceAvailability, ResourceVector
from business_master.policies.portfolio import PortfolioPolicy
from business_master.storage.beliefs_postgres import PostgresBeliefStore
from business_master.storage.capital_postgres import (
    CapitalAuthorizationConflictError,
    CapitalAuthorizationDeniedError,
    PostgresCapitalAuthorizationStore,
)
from business_master.storage.economic_ledger_postgres import PostgresEconomicLedgerStore
from business_master.storage.experiment_contracts_postgres import PostgresExperimentContractStore
from business_master.storage.family_evaluations_postgres import PostgresFamilyEvaluationStore
from business_master.storage.portfolio_postgres import PostgresPortfolioStore

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


def _fund_cash(dsn: str, amount: Decimal, currency: str) -> None:
    PostgresEconomicLedgerStore(dsn).record(
        LedgerTransactionRequest(
            idempotency_key=f"fund:{currency}:{amount}:{uuid4()}",
            occurred_at=NOW - timedelta(hours=1),
            description=f"Fund {currency} cash for capital tests",
            postings=(
                LedgerPosting(
                    account=LedgerAccount.CASH,
                    side=LedgerSide.DEBIT,
                    amount=amount,
                    currency=currency,
                ),
                LedgerPosting(
                    account=LedgerAccount.EQUITY,
                    side=LedgerSide.CREDIT,
                    amount=amount,
                    currency=currency,
                ),
            ),
        )
    )


def _seed_allocations(
    dsn: str,
    amounts: tuple[Decimal, ...],
    *,
    currency: str = "USD",
):
    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.ACQUISITION,
        subject="capital-control candidate",
        proposition="Paid bounded acquisition creates useful evidence",
    )
    PostgresBeliefStore(dsn).save_economic_hypothesis(hypothesis)

    contract = ExperimentContract(
        economic_hypothesis_id=hypothesis.id,
        business_family="content",
        question="Does bounded paid acquisition create signal?",
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
        resource_requirements=ResourceVector(),
    )
    PostgresExperimentContractStore(dsn).save_contract(contract)

    evaluation = FamilyEvaluation(
        id=uuid4(),
        idempotency_key=f"capital-family-eval-{uuid4()}",
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
        rationale="bounded paid probe is eligible for portfolio consideration",
        evaluated_at=NOW,
    )
    PostgresFamilyEvaluationStore(dsn).save(evaluation)

    candidates = tuple(
        PortfolioCandidate(
            family_evaluation=evaluation,
            contract=contract,
            roles=(PortfolioRole.SIGNAL,),
            value=PortfolioValueEstimate(information_value=0.8, feedback_speed=0.8),
            capital_requirement=CapitalRequirement(
                amount=amount,
                currency=currency,
                category=SpendCategory.PAID_ADS,
            ),
            group_key=f"paid-probe-{index}",
        )
        for index, amount in enumerate(amounts)
    )
    plan = PortfolioPolicy().plan(
        PortfolioPlanRequest(
            idempotency_key=f"capital-plan-{uuid4()}",
            candidates=candidates,
            availability=ResourceAvailability(
                capacity=ResourceVector(),
                reserved=ResourceVector(),
                available=ResourceVector(),
            ),
            base_currency=currency,
            max_candidates=len(candidates),
            exploration_fraction=0.0,
            max_group_fraction=1.0,
            created_at=NOW,
        )
    )
    PostgresPortfolioStore(dsn).save(plan)
    assert len(plan.allocations) == len(amounts)
    return hypothesis, evaluation, plan.allocations


def _request(allocation, *, key: str, risk: RiskLevel = RiskLevel.LOW):
    capital = allocation.capital_requirement
    assert capital is not None
    return CapitalAuthorizationRequest(
        idempotency_key=key,
        portfolio_allocation_id=allocation.id,
        family_evaluation_id=allocation.family_evaluation_id,
        hypothesis_id=allocation.hypothesis_id,
        amount=capital.amount,
        currency=capital.currency,
        category=capital.category,
        stage=CapitalStage.PROBE,
        risk=risk,
        requested_at=NOW,
        expires_at=NOW + timedelta(hours=1),
    )


def _envelope(
    *,
    currency: str = "USD",
    max_per: Decimal = Decimal("100"),
    max_outstanding: Decimal = Decimal("100"),
    hard_ceiling: Decimal | None = None,
) -> CapitalEnvelope:
    return CapitalEnvelope(
        currency=currency,
        stage=CapitalStage.PROBE,
        max_per_authorization=max_per,
        max_outstanding=max_outstanding,
        max_risk=RiskLevel.MEDIUM,
        operator_hard_ceiling=hard_ceiling,
        period_start=None if hard_ceiling is None else NOW,
        period_end=None if hard_ceiling is None else NOW + timedelta(days=1),
    )


def test_concurrent_authorizations_cannot_claim_same_cash(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(
        postgres_dsn,
        (Decimal("60"), Decimal("60")),
    )
    barrier = Barrier(2)

    def attempt(index: int) -> bool:
        store = PostgresCapitalAuthorizationStore(postgres_dsn)
        request = _request(allocations[index], key=f"concurrent-capital-{index}")
        barrier.wait()
        try:
            store.authorize(request, _envelope())
        except CapitalAuthorizationDeniedError:
            return False
        return True

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(attempt, [0, 1]))

    assert sorted(results) == [False, True]
    with psycopg.connect(postgres_dsn) as conn:
        row = conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(amount), 0) "
            "FROM capital_authorization WHERE status = 'active'"
        ).fetchone()
    assert row == (1, Decimal("60"))


def test_capital_authorization_is_retry_idempotent_and_conflict_safe(
    postgres_dsn: str,
) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("40"),))
    request = _request(allocations[0], key="capital-idempotent")
    store = PostgresCapitalAuthorizationStore(postgres_dsn)

    first = store.authorize(request, _envelope())
    retry = store.authorize(request, _envelope())
    assert retry == first

    conflicting = request.model_copy(update={"risk": RiskLevel.MEDIUM})
    with pytest.raises(CapitalAuthorizationConflictError, match="different semantics"):
        store.authorize(conflicting, _envelope())


def test_operator_zero_ceiling_blocks_ledger_funded_spend(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("1000"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("10"),))

    with pytest.raises(CapitalAuthorizationDeniedError, match="operator hard ceiling"):
        PostgresCapitalAuthorizationStore(postgres_dsn).authorize(
            _request(allocations[0], key="zero-ceiling"),
            _envelope(hard_ceiling=Decimal(0)),
        )


def test_release_and_expiry_restore_authorization_capacity(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(
        postgres_dsn,
        (Decimal("60"), Decimal("60")),
    )
    store = PostgresCapitalAuthorizationStore(postgres_dsn)

    first = store.authorize(
        _request(allocations[0], key="release-first"),
        _envelope(),
    )
    released = store.release(first.id)
    released_again = store.release(first.id)
    assert released.status is CapitalAuthorizationStatus.RELEASED
    assert released_again == released

    second_request = _request(allocations[1], key="expire-second")
    second = store.authorize(second_request, _envelope())
    expired = store.expire(second.id, as_of=NOW + timedelta(hours=2))
    expired_again = store.expire(second.id, as_of=NOW + timedelta(hours=2))
    assert expired.status is CapitalAuthorizationStatus.EXPIRED
    assert expired_again == expired


def test_currency_isolation_prevents_using_other_currency_cash(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _fund_cash(postgres_dsn, Decimal("1000"), "EUR")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("120"),), currency="USD")

    with pytest.raises(CapitalAuthorizationDeniedError, match="ledger cash"):
        PostgresCapitalAuthorizationStore(postgres_dsn).authorize(
            _request(allocations[0], key="currency-isolation"),
            _envelope(max_per=Decimal("200"), max_outstanding=Decimal("200")),
        )


def test_consumption_requires_ledger_lineage_and_preserves_history(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("40"),))
    store = PostgresCapitalAuthorizationStore(postgres_dsn)
    authorization = store.authorize(
        _request(allocations[0], key="consume-capital"),
        _envelope(),
    )

    transaction = PostgresEconomicLedgerStore(postgres_dsn).record(
        LedgerTransactionRequest(
            idempotency_key="consume-capital-ledger",
            occurred_at=NOW + timedelta(minutes=5),
            description="Consume bounded paid acquisition authorization",
            postings=(
                LedgerPosting(
                    account=LedgerAccount.ACQUISITION_SPEND,
                    side=LedgerSide.DEBIT,
                    amount=Decimal("40"),
                    currency="USD",
                ),
                LedgerPosting(
                    account=LedgerAccount.CASH,
                    side=LedgerSide.CREDIT,
                    amount=Decimal("40"),
                    currency="USD",
                ),
            ),
        )
    )
    consumed = store.consume(
        authorization.id,
        transaction.id,
        as_of=NOW + timedelta(minutes=5),
    )

    assert consumed.status is CapitalAuthorizationStatus.CONSUMED
    assert consumed.ledger_transaction_id == transaction.id
    assert store.get(authorization.id) == consumed
