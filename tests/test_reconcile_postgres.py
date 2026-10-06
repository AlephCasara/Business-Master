from __future__ import annotations

import os
from pathlib import Path

import psycopg
import pytest

from business_master.controllers.reconcile_service import ReconcileService
from business_master.domain.models import Hypothesis
from business_master.storage.postgres import PostgresStore
from business_master.storage.reconcile_postgres import PostgresReconcileStore


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


def test_reconcile_creates_exactly_one_probe_across_restart(postgres_dsn: str) -> None:
    hypothesis = Hypothesis(
        name="chart-content-probe",
        thesis="Useful chart shorts can earn external attention",
        family="content",
    )
    PostgresStore(postgres_dsn).save_hypothesis(hypothesis)

    first_process = ReconcileService(PostgresReconcileStore(postgres_dsn))
    first = first_process.run_once(available_probe_slots=1)

    assert len(first.created_experiment_ids) == 1

    # A brand-new service/store object simulates the control process restarting.
    second_process = ReconcileService(PostgresReconcileStore(postgres_dsn))
    second = second_process.run_once(available_probe_slots=1)

    assert second.created_experiment_ids == ()

    with psycopg.connect(postgres_dsn) as conn:
        experiment_count = conn.execute(
            "SELECT count(*) FROM experiment WHERE hypothesis_id = %s",
            (hypothesis.id,),
        ).fetchone()
        action_count = conn.execute(
            """
            SELECT count(*)
            FROM action_intent
            WHERE entity_id = %s AND action_type = 'create_probe'
            """,
            (hypothesis.id,),
        ).fetchone()
        decision_count = conn.execute(
            """
            SELECT count(*)
            FROM decision
            WHERE entity_id = %s AND decision_type = 'create_probe'
            """,
            (hypothesis.id,),
        ).fetchone()

    assert experiment_count is not None and experiment_count[0] == 1
    assert action_count is not None and action_count[0] == 1
    assert decision_count is not None and decision_count[0] == 1
