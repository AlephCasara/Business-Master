from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import psycopg
import pytest

from business_master.domain.ledger import (
    LedgerAccount,
    LedgerPosting,
    LedgerSide,
    LedgerTransactionRequest,
)
from business_master.storage.economic_ledger_postgres import (
    LedgerTransactionConflictError,
    PostgresEconomicLedgerStore,
)


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


def _posting(
    account: LedgerAccount,
    side: LedgerSide,
    amount: str,
    currency: str = "USD",
) -> LedgerPosting:
    return LedgerPosting(
        account=account,
        side=side,
        amount=Decimal(amount),
        currency=currency,
    )


def _request(
    key: str,
    description: str,
    postings: tuple[LedgerPosting, ...],
    *,
    occurred_at: datetime,
    experiment_id: UUID | None = None,
    offer_id: UUID | None = None,
    channel_id: UUID | None = None,
) -> LedgerTransactionRequest:
    return LedgerTransactionRequest(
        idempotency_key=key,
        occurred_at=occurred_at,
        description=description,
        postings=postings,
        experiment_id=experiment_id,
        offer_id=offer_id,
        channel_id=channel_id,
    )


def _seed_attribution(dsn: str) -> tuple[UUID, UUID, UUID]:
    hypothesis_id = uuid4()
    experiment_id = uuid4()
    channel_id = uuid4()
    offer_id = uuid4()
    with psycopg.connect(dsn) as conn:
        conn.execute(
            "INSERT INTO hypothesis (id, name, thesis, family) VALUES (%s, %s, %s, %s)",
            (hypothesis_id, "ledger test", "economic truth", "test"),
        )
        conn.execute(
            "INSERT INTO channel (id, platform, name) VALUES (%s, %s, %s)",
            (channel_id, "test", "ledger-channel"),
        )
        conn.execute(
            """
            INSERT INTO experiment (id, hypothesis_id, business_family, channel_id)
            VALUES (%s, %s, %s, %s)
            """,
            (experiment_id, hypothesis_id, "test", channel_id),
        )
    return experiment_id, offer_id, channel_id


def test_record_is_idempotent_and_conflicts_on_semantic_change(postgres_dsn: str) -> None:
    store = PostgresEconomicLedgerStore(postgres_dsn)
    occurred_at = datetime(2026, 10, 7, tzinfo=UTC)
    request = _request(
        "funding:bootstrap",
        "Bootstrap capital",
        (
            _posting(LedgerAccount.CASH, LedgerSide.DEBIT, "1000"),
            _posting(LedgerAccount.EQUITY, LedgerSide.CREDIT, "1000"),
        ),
        occurred_at=occurred_at,
    )

    first = store.record(request)
    duplicate = store.record(request)

    assert duplicate.id == first.id
    assert store.get(first.id) == first

    changed = request.model_copy(update={"description": "Different economic event"})
    with pytest.raises(LedgerTransactionConflictError, match="idempotency key"):
        store.record(changed)


def test_snapshot_tracks_settlement_costs_working_capital_and_attribution(
    postgres_dsn: str,
) -> None:
    store = PostgresEconomicLedgerStore(postgres_dsn)
    experiment_id, offer_id, channel_id = _seed_attribution(postgres_dsn)
    t0 = datetime(2026, 10, 7, tzinfo=UTC)

    events = [
        _request(
            "capital:usd",
            "Fund USD cash",
            (
                _posting(LedgerAccount.CASH, LedgerSide.DEBIT, "1000"),
                _posting(LedgerAccount.EQUITY, LedgerSide.CREDIT, "1000"),
            ),
            occurred_at=t0,
        ),
        _request(
            "sale:recognized",
            "Recognize customer receivable",
            (
                _posting(LedgerAccount.ACCOUNTS_RECEIVABLE, LedgerSide.DEBIT, "200"),
                _posting(LedgerAccount.REVENUE, LedgerSide.CREDIT, "200"),
            ),
            occurred_at=t0 + timedelta(minutes=1),
            experiment_id=experiment_id,
            offer_id=offer_id,
            channel_id=channel_id,
        ),
        _request(
            "sale:settled",
            "Settle receivable into cash",
            (
                _posting(LedgerAccount.CASH, LedgerSide.DEBIT, "200"),
                _posting(LedgerAccount.ACCOUNTS_RECEIVABLE, LedgerSide.CREDIT, "200"),
            ),
            occurred_at=t0 + timedelta(minutes=2),
            experiment_id=experiment_id,
            offer_id=offer_id,
            channel_id=channel_id,
        ),
        _request(
            "fee:platform",
            "Platform fee",
            (
                _posting(LedgerAccount.FEES, LedgerSide.DEBIT, "20"),
                _posting(LedgerAccount.CASH, LedgerSide.CREDIT, "20"),
            ),
            occurred_at=t0 + timedelta(minutes=3),
            experiment_id=experiment_id,
            offer_id=offer_id,
            channel_id=channel_id,
        ),
        _request(
            "cost:payable",
            "Direct fulfillment cost payable",
            (
                _posting(LedgerAccount.DIRECT_COSTS, LedgerSide.DEBIT, "50"),
                _posting(LedgerAccount.ACCOUNTS_PAYABLE, LedgerSide.CREDIT, "50"),
            ),
            occurred_at=t0 + timedelta(minutes=4),
            experiment_id=experiment_id,
            offer_id=offer_id,
            channel_id=channel_id,
        ),
        _request(
            "acquisition:cash",
            "Acquisition spend",
            (
                _posting(LedgerAccount.ACQUISITION_SPEND, LedgerSide.DEBIT, "30"),
                _posting(LedgerAccount.CASH, LedgerSide.CREDIT, "30"),
            ),
            occurred_at=t0 + timedelta(minutes=5),
            experiment_id=experiment_id,
            offer_id=offer_id,
            channel_id=channel_id,
        ),
        _request(
            "refund:cash",
            "Customer refund",
            (
                _posting(LedgerAccount.REFUNDS_RETURNS, LedgerSide.DEBIT, "25"),
                _posting(LedgerAccount.CASH, LedgerSide.CREDIT, "25"),
            ),
            occurred_at=t0 + timedelta(minutes=6),
            experiment_id=experiment_id,
            offer_id=offer_id,
            channel_id=channel_id,
        ),
        _request(
            "working-capital:inventory",
            "Acquire working-capital asset",
            (
                _posting(LedgerAccount.WORKING_CAPITAL_ASSET, LedgerSide.DEBIT, "100"),
                _posting(LedgerAccount.CASH, LedgerSide.CREDIT, "100"),
            ),
            occurred_at=t0 + timedelta(minutes=7),
            experiment_id=experiment_id,
            offer_id=offer_id,
            channel_id=channel_id,
        ),
    ]
    for event in events:
        store.record(event)

    snapshot = store.snapshot("USD")
    assert snapshot.cash_available == Decimal("1025")
    assert snapshot.receivables == Decimal("0")
    assert snapshot.payables == Decimal("50")
    assert snapshot.working_capital_assets == Decimal("100")
    assert snapshot.working_capital_exposure == Decimal("50")
    assert snapshot.recognized_revenue == Decimal("200")
    assert snapshot.refunds_returns == Decimal("25")
    assert snapshot.fees == Decimal("20")
    assert snapshot.direct_costs == Decimal("50")
    assert snapshot.acquisition_spend == Decimal("30")
    assert snapshot.contribution_margin == Decimal("105")
    assert snapshot.contribution_after_acquisition == Decimal("75")

    attributed = store.snapshot("USD", experiment_id=experiment_id)
    assert attributed.recognized_revenue == Decimal("200")
    assert attributed.contribution_after_acquisition == Decimal("75")

    offer_transactions = store.list_transactions(currency="USD", offer_id=offer_id)
    channel_transactions = store.list_transactions(currency="USD", channel_id=channel_id)
    assert len(offer_transactions) == 7
    assert len(channel_transactions) == 7


def test_currency_snapshots_never_silently_mix(postgres_dsn: str) -> None:
    store = PostgresEconomicLedgerStore(postgres_dsn)
    occurred_at = datetime(2026, 10, 7, tzinfo=UTC)

    store.record(
        _request(
            "capital:usd",
            "USD capital",
            (
                _posting(LedgerAccount.CASH, LedgerSide.DEBIT, "100", "USD"),
                _posting(LedgerAccount.EQUITY, LedgerSide.CREDIT, "100", "USD"),
            ),
            occurred_at=occurred_at,
        )
    )
    store.record(
        _request(
            "capital:eur",
            "EUR capital",
            (
                _posting(LedgerAccount.CASH, LedgerSide.DEBIT, "80", "EUR"),
                _posting(LedgerAccount.EQUITY, LedgerSide.CREDIT, "80", "EUR"),
            ),
            occurred_at=occurred_at + timedelta(seconds=1),
        )
    )

    assert store.snapshot("USD").cash_available == Decimal("100")
    assert store.snapshot("EUR").cash_available == Decimal("80")
