from __future__ import annotations

import os
from pathlib import Path

import psycopg
import pytest

from business_master.domain.beliefs import BeliefState, FreshnessPolicy
from business_master.domain.enums import FreshnessMode, HypothesisType
from business_master.domain.hypotheses import (
    BeliefContext,
    EconomicHypothesis,
    EvidenceRequirements,
    Hypothesis,
)
from business_master.storage.beliefs_postgres import PostgresBeliefStore
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


def test_economic_hypothesis_and_belief_roundtrip(postgres_dsn: str) -> None:
    legacy = Hypothesis(
        name="legacy-offer",
        thesis="A productized offer can convert",
        family="b2b",
        market="US",
        audience="agencies",
    )
    PostgresStore(postgres_dsn).save_hypothesis(legacy)

    store = PostgresBeliefStore(postgres_dsn)
    parent = EconomicHypothesis(
        hypothesis_type=HypothesisType.DEMAND,
        subject="agency automation demand",
        proposition="US agencies have recurring automation pain",
    )
    dependency = EconomicHypothesis(
        hypothesis_type=HypothesisType.CAPABILITY,
        subject="delivery capability",
        proposition="The factory can fulfill the service with low human time",
    )
    store.save_economic_hypothesis(parent)
    store.save_economic_hypothesis(dependency)

    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.OFFER,
        subject="productized agency automation",
        proposition="Agencies will buy a fixed-scope automation package",
        mechanism="Reduce repetitive operational work with bounded automation",
        context=BeliefContext(
            market="US",
            audience="agencies",
            geography="United States",
            language="en",
            channel="outbound",
            dimensions={"price_band": "mid_ticket"},
        ),
        expected_observation="Qualified agencies accept paid pilots",
        falsification_condition="No paid pilots after sufficient qualified exposure",
        evidence_requirements=EvidenceRequirements(
            minimum_count=3,
            minimum_independent_sources=2,
            required_kinds=["reply", "payment"],
        ),
        measurement_window_seconds=604800,
        freshness_policy=FreshnessPolicy(mode=FreshnessMode.TTL, ttl_seconds=2592000),
        parent_ids=[parent.id],
        dependency_ids=[dependency.id],
        legacy_hypothesis_id=legacy.id,
    )
    store.save_economic_hypothesis(hypothesis)

    restored = store.get_economic_hypothesis(hypothesis.id)

    assert restored == hypothesis

    belief = BeliefState(
        hypothesis_id=hypothesis.id,
        confidence=0.35,
        uncertainty=0.65,
        evidence_count=2,
        freshness=0.9,
    )
    store.save_belief_state(belief)
    restored_belief = store.get_belief_state(hypothesis.id)

    assert restored_belief == belief

    updated_belief = belief.model_copy(
        update={
            "confidence": 0.6,
            "uncertainty": 0.4,
            "evidence_count": 4,
            "state_version": 2,
        }
    )
    store.save_belief_state(updated_belief)

    assert store.get_belief_state(hypothesis.id) == updated_belief
