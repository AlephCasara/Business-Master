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


class MutableClock:
    def __init__(self, value: datetime) -> None:
        self.value = value

    def __call__(self) -> datetime:
        return self.value


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


def _store(dsn: str, clock: MutableClock | None = None) -> PostgresCapitalAuthorizationStore:
    effective_clock = clock or MutableClock(NOW)
    return PostgresCapitalAuthorizationStore(dsn, clock=effective_clock)


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


def _request(
    allocation,
    *,
    key: str,
    risk: RiskLevel = RiskLevel.LOW,
    blast_radius: float = 0.0,
    reversible: bool = True,
    human_gate_required: bool = False,
    stage: CapitalStage = CapitalStage.PROBE,
    requested_at: datetime = NOW,
    expires_at: datetime | None = None,
):
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
        stage=stage,
        risk=risk,
        blast_radius=blast_radius,
        reversible=reversible,
        human_gate_required=human_gate_required,
        requested_at=requested_at,
        expires_at=expires_at or requested_at + timedelta(hours=1),
    )


def _envelope(
    *,
    currency: str = "USD",
    max_per: Decimal = Decimal("100"),
    max_outstanding: Decimal = Decimal("100"),
    hard_ceiling: Decimal | None = None,
    stage: CapitalStage = CapitalStage.PROBE,
) -> CapitalEnvelope:
    return CapitalEnvelope(
        currency=currency,
        stage=stage,
        max_per_authorization=max_per,
        max_outstanding=max_outstanding,
        max_risk=RiskLevel.MEDIUM,
        max_blast_radius=1.0,
        operator_hard_ceiling=hard_ceiling,
        period_start=None if hard_ceiling is None else NOW,
        period_end=None if hard_ceiling is None else NOW + timedelta(days=1),
    )


def _record_spend(
    dsn: str,
    authorization_id,
    *,
    amount: Decimal,
    occurred_at: datetime,
    link_authorization: bool = True,
):
    metadata = (
        {"capital_authorization_id": str(authorization_id)}
        if link_authorization
        else {}
    )
    return PostgresEconomicLedgerStore(dsn).record(
        LedgerTransactionRequest(
            idempotency_key=f"spend:{uuid4()}",
            occurred_at=occurred_at,
            description="Consume bounded paid acquisition authorization",
            postings=(
                LedgerPosting(
                    account=LedgerAccount.ACQUISITION_SPEND,
                    side=LedgerSide.DEBIT,
                    amount=amount,
                    currency="USD",
                ),
                LedgerPosting(
                    account=LedgerAccount.CASH,
                    side=LedgerSide.CREDIT,
                    amount=amount,
                    currency="USD",
                ),
            ),
            metadata=metadata,
        )
    )


def test_portfolio_allocation_does_not_authorize_or_spend_capital(postgres_dsn: str) -> None:
    _seed_allocations(postgres_dsn, (Decimal("10"),))

    with psycopg.connect(postgres_dsn) as conn:
        authorization_count = conn.execute(
            "SELECT COUNT(*) FROM capital_authorization"
        ).fetchone()
        ledger_count = conn.execute(
            "SELECT COUNT(*) FROM economic_ledger_transaction"
        ).fetchone()

    assert authorization_count == (0,)
    assert ledger_count == (0,)


def test_authorization_itself_does_not_create_ledger_spend(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("25"),))
    with psycopg.connect(postgres_dsn) as conn:
        before = conn.execute("SELECT COUNT(*) FROM economic_ledger_transaction").fetchone()

    authorization = _store(postgres_dsn).authorize(
        _request(allocations[0], key="authorize-no-spend"),
        _envelope(),
    )

    with psycopg.connect(postgres_dsn) as conn:
        after = conn.execute("SELECT COUNT(*) FROM economic_ledger_transaction").fetchone()
    assert authorization.status is CapitalAuthorizationStatus.ACTIVE
    assert authorization.blast_radius == 0.0
    assert authorization.reversible is True
    assert authorization.human_gate_required is False
    assert before == after


def test_concurrent_authorizations_cannot_claim_same_cash(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(
        postgres_dsn,
        (Decimal("60"), Decimal("60")),
    )
    barrier = Barrier(2)

    def attempt(index: int) -> bool:
        store = _store(postgres_dsn)
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
    clock = MutableClock(NOW)
    store = _store(postgres_dsn, clock)

    first = store.authorize(request, _envelope())
    clock.value = NOW + timedelta(minutes=10)
    retry = store.authorize(request, _envelope())
    assert retry == first
    assert first.requested_at == NOW
    assert first.authorized_at == NOW

    conflicting = request.model_copy(update={"risk": RiskLevel.MEDIUM})
    with pytest.raises(CapitalAuthorizationConflictError, match="different semantics"):
        store.authorize(conflicting, _envelope())


def test_request_timestamp_cannot_expire_existing_authorization(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(
        postgres_dsn,
        (Decimal("60"), Decimal("60")),
    )
    store = _store(postgres_dsn, MutableClock(NOW))
    first = store.authorize(
        _request(allocations[0], key="trusted-clock-first"),
        _envelope(),
    )
    future_request = _request(
        allocations[1],
        key="untrusted-future-request",
        requested_at=NOW + timedelta(hours=2),
        expires_at=NOW + timedelta(hours=3),
    )

    with pytest.raises(CapitalAuthorizationDeniedError, match="ledger cash"):
        store.authorize(future_request, _envelope())

    assert store.get(first.id).status is CapitalAuthorizationStatus.ACTIVE  # type: ignore[union-attr]


def test_operator_zero_ceiling_blocks_ledger_funded_spend(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("1000"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("10"),))

    with pytest.raises(CapitalAuthorizationDeniedError, match="operator hard ceiling"):
        _store(postgres_dsn).authorize(
            _request(allocations[0], key="zero-ceiling"),
            _envelope(hard_ceiling=Decimal(0)),
        )


def test_release_and_expiry_restore_authorization_capacity(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(
        postgres_dsn,
        (Decimal("60"), Decimal("60")),
    )
    clock = MutableClock(NOW)
    store = _store(postgres_dsn, clock)

    first = store.authorize(
        _request(allocations[0], key="release-first"),
        _envelope(),
    )
    released = store.release(first.id)
    released_again = store.release(first.id)
    assert released.status is CapitalAuthorizationStatus.RELEASED
    assert released_again == released

    second = store.authorize(
        _request(allocations[1], key="expire-second"),
        _envelope(),
    )
    clock.value = NOW + timedelta(hours=2)
    expired = store.expire(second.id)
    expired_again = store.expire(second.id)
    assert expired.status is CapitalAuthorizationStatus.EXPIRED
    assert expired_again == expired


def test_release_after_expiry_preserves_expired_semantics(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("20"),))
    clock = MutableClock(NOW)
    store = _store(postgres_dsn, clock)
    authorization = store.authorize(
        _request(allocations[0], key="late-release"),
        _envelope(),
    )

    clock.value = NOW + timedelta(hours=2)
    terminal = store.release(authorization.id)

    assert terminal.status is CapitalAuthorizationStatus.EXPIRED
    assert terminal.expired_at == clock.value
    assert terminal.released_at == clock.value


def test_terminal_authorization_requires_replan_for_same_allocation(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("20"),))
    store = _store(postgres_dsn)
    first = store.authorize(
        _request(allocations[0], key="one-shot-first"),
        _envelope(),
    )
    store.release(first.id)

    with pytest.raises(CapitalAuthorizationConflictError, match="replan"):
        store.authorize(
            _request(allocations[0], key="one-shot-second"),
            _envelope(),
        )


def test_currency_isolation_prevents_using_other_currency_cash(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _fund_cash(postgres_dsn, Decimal("1000"), "EUR")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("120"),), currency="USD")

    with pytest.raises(CapitalAuthorizationDeniedError, match="ledger cash"):
        _store(postgres_dsn).authorize(
            _request(allocations[0], key="currency-isolation"),
            _envelope(max_per=Decimal("200"), max_outstanding=Decimal("200")),
        )


def test_capital_store_rejects_tampered_portfolio_base_currency(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("25"),), currency="USD")
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute("UPDATE portfolio_plan SET base_currency = 'EUR'")

    with pytest.raises(ValueError, match="portfolio base currency"):
        _store(postgres_dsn).authorize(
            _request(allocations[0], key="tampered-base-currency"),
            _envelope(),
        )


def test_capital_store_rejects_understated_allocation_risk(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("25"),))
    with psycopg.connect(postgres_dsn) as conn:
        conn.execute(
            "UPDATE portfolio_allocation "
            "SET risk_assessment = jsonb_set(risk_assessment, '{level}', '\"medium\"')"
        )

    with pytest.raises(ValueError, match="risk differs"):
        _store(postgres_dsn).authorize(
            _request(allocations[0], key="understated-risk"),
            _envelope(),
        )


def test_capital_store_rejects_tampered_blast_radius(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("25"),))

    with pytest.raises(ValueError, match="blast radius differs"):
        _store(postgres_dsn).authorize(
            _request(
                allocations[0],
                key="tampered-blast-radius",
                blast_radius=0.5,
            ),
            _envelope(),
        )


def test_probe_allocation_cannot_escalate_directly_to_scale_capital(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("25"),))

    with pytest.raises(ValueError, match="stage exceeds"):
        _store(postgres_dsn).authorize(
            _request(
                allocations[0],
                key="probe-to-scale",
                stage=CapitalStage.SCALE,
            ),
            _envelope(stage=CapitalStage.SCALE),
        )


def test_consumption_requires_explicit_ledger_authorization_lineage(
    postgres_dsn: str,
) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("40"),))
    clock = MutableClock(NOW)
    store = _store(postgres_dsn, clock)
    authorization = store.authorize(
        _request(allocations[0], key="missing-ledger-lineage"),
        _envelope(),
    )
    transaction = _record_spend(
        postgres_dsn,
        authorization.id,
        amount=Decimal("40"),
        occurred_at=NOW + timedelta(minutes=5),
        link_authorization=False,
    )
    clock.value = NOW + timedelta(minutes=5)

    with pytest.raises(ValueError, match="not linked"):
        store.consume(authorization.id, transaction.id)

    assert store.get(authorization.id).status is CapitalAuthorizationStatus.ACTIVE  # type: ignore[union-attr]


def test_consumption_requires_exact_authorized_cash_outflow(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("40"),))
    clock = MutableClock(NOW)
    store = _store(postgres_dsn, clock)
    authorization = store.authorize(
        _request(allocations[0], key="wrong-cash-outflow"),
        _envelope(),
    )
    transaction = _record_spend(
        postgres_dsn,
        authorization.id,
        amount=Decimal("39"),
        occurred_at=NOW + timedelta(minutes=5),
    )
    clock.value = NOW + timedelta(minutes=5)

    with pytest.raises(ValueError, match="cash outflow does not match"):
        store.consume(authorization.id, transaction.id)


def test_consumption_rejects_spend_event_after_expiry(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("40"),))
    clock = MutableClock(NOW)
    store = _store(postgres_dsn, clock)
    authorization = store.authorize(
        _request(allocations[0], key="late-spend"),
        _envelope(),
    )
    transaction = _record_spend(
        postgres_dsn,
        authorization.id,
        amount=Decimal("40"),
        occurred_at=NOW + timedelta(hours=1),
    )
    clock.value = NOW + timedelta(hours=1, minutes=1)

    with pytest.raises(ValueError, match="after authorization expiry"):
        store.consume(authorization.id, transaction.id)


def test_consumption_requires_ledger_lineage_and_preserves_history(postgres_dsn: str) -> None:
    _fund_cash(postgres_dsn, Decimal("100"), "USD")
    _, _, allocations = _seed_allocations(postgres_dsn, (Decimal("40"),))
    clock = MutableClock(NOW)
    store = _store(postgres_dsn, clock)
    authorization = store.authorize(
        _request(allocations[0], key="consume-capital"),
        _envelope(),
    )
    transaction = _record_spend(
        postgres_dsn,
        authorization.id,
        amount=Decimal("40"),
        occurred_at=NOW + timedelta(minutes=5),
    )
    clock.value = NOW + timedelta(minutes=5)

    consumed = store.consume(authorization.id, transaction.id)

    assert consumed.status is CapitalAuthorizationStatus.CONSUMED
    assert consumed.ledger_transaction_id == transaction.id
    assert consumed.requested_at == NOW
    assert consumed.authorized_at == NOW
    assert store.get(authorization.id) == consumed
