from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path

import psycopg
import pytest

from business_master.domain.belief_updates import (
    BeliefUpdateRequest,
    EvidenceInterpretation,
)
from business_master.domain.beliefs import FreshnessPolicy
from business_master.domain.enums import (
    EvidenceClass,
    EvidenceProvenance,
    EvidenceTargetKind,
    FreshnessMode,
    HypothesisType,
)
from business_master.domain.evidence import EvidenceAssociation, EvidenceRecord
from business_master.domain.hypotheses import EconomicHypothesis
from business_master.storage.belief_updates_postgres import PostgresBeliefUpdateEngine
from business_master.storage.beliefs_postgres import PostgresBeliefStore
from business_master.storage.evidence_postgres import PostgresEvidenceStore


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


def _record(
    *,
    evidence_class: EvidenceClass,
    observed_at: datetime,
    kind: str,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_class=evidence_class,
        provenance=EvidenceProvenance.OBSERVED_OWN,
        kind=kind,
        source="pr7-test",
        source_event_id=f"{kind}-{observed_at.isoformat()}",
        observed_at=observed_at,
    )


def _persist_and_bind(
    store: PostgresEvidenceStore,
    hypothesis: EconomicHypothesis,
    record: EvidenceRecord,
) -> None:
    store.save_record(record)
    store.bind_record(
        EvidenceAssociation(
            evidence_id=record.id,
            target_kind=EvidenceTargetKind.ECONOMIC_HYPOTHESIS,
            target_id=hypothesis.id,
        )
    )


def test_evidence_updates_create_immutable_belief_history(postgres_dsn: str) -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    belief_store = PostgresBeliefStore(postgres_dsn)
    evidence_store = PostgresEvidenceStore(postgres_dsn)
    engine = PostgresBeliefUpdateEngine(postgres_dsn)

    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.DEMAND,
        subject="qualified outbound demand",
        proposition="Qualified prospects respond to the productized offer",
        freshness_policy=FreshnessPolicy(mode=FreshnessMode.TTL, ttl_seconds=100),
    )
    belief_store.save_economic_hypothesis(hypothesis)

    supporting = _record(
        evidence_class=EvidenceClass.MARKET,
        observed_at=now,
        kind="qualified_reply",
    )
    _persist_and_bind(evidence_store, hypothesis, supporting)

    request = BeliefUpdateRequest(
        hypothesis_id=hypothesis.id,
        evidence_id=supporting.id,
        interpretation=EvidenceInterpretation.SUPPORTING,
        strength=0.8,
        rationale="Qualified reply supports demand",
        evaluated_at=now,
    )
    first = engine.apply(request)

    assert first.update.applied is True
    assert first.update.prior_state_version == 1
    assert first.update.resulting_state_version == 2
    assert first.state.state_version == 2
    assert first.state.confidence == pytest.approx(0.4)
    assert first.state.uncertainty == pytest.approx(0.6)
    assert first.state.evidence_count == 1
    assert belief_store.get_belief_state(hypothesis.id) == first.state

    history = engine.list_state_history(hypothesis.id)
    assert [state.state_version for state in history] == [1, 2]
    assert history[0].evidence_count == 0
    assert history[1] == first.state

    retry = engine.apply(request)
    assert retry.update.id == first.update.id
    assert retry.state == first.state
    assert len(engine.list_state_history(hypothesis.id)) == 2
    assert len(engine.list_updates(hypothesis.id)) == 1

    conflicting_retry = request.model_copy(
        update={
            "interpretation": EvidenceInterpretation.FALSIFYING,
            "rationale": "Changed semantics",
        }
    )
    with pytest.raises(ValueError, match="different update semantics"):
        engine.apply(conflicting_retry)

    falsifying = _record(
        evidence_class=EvidenceClass.MARKET,
        observed_at=now + timedelta(seconds=10),
        kind="qualified_rejection",
    )
    _persist_and_bind(evidence_store, hypothesis, falsifying)
    second = engine.apply(
        BeliefUpdateRequest(
            hypothesis_id=hypothesis.id,
            evidence_id=falsifying.id,
            interpretation=EvidenceInterpretation.FALSIFYING,
            strength=1.0,
            rationale="Qualified rejection falsifies demand",
            evaluated_at=now + timedelta(seconds=10),
        )
    )

    assert second.state.state_version == 3
    assert second.state.confidence == pytest.approx(0.2)
    assert second.state.uncertainty == pytest.approx(0.3)
    assert second.state.evidence_count == 2
    assert [state.state_version for state in engine.list_state_history(hypothesis.id)] == [
        1,
        2,
        3,
    ]


def test_technical_and_stale_evidence_are_audited_but_not_applied(
    postgres_dsn: str,
) -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    belief_store = PostgresBeliefStore(postgres_dsn)
    evidence_store = PostgresEvidenceStore(postgres_dsn)
    engine = PostgresBeliefUpdateEngine(postgres_dsn)

    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.OFFER,
        subject="offer conversion",
        proposition="The offer converts qualified demand",
        freshness_policy=FreshnessPolicy(mode=FreshnessMode.TTL, ttl_seconds=60),
    )
    belief_store.save_economic_hypothesis(hypothesis)

    technical = _record(
        evidence_class=EvidenceClass.TECHNICAL,
        observed_at=now,
        kind="renderer_failed",
    )
    _persist_and_bind(evidence_store, hypothesis, technical)
    technical_result = engine.apply(
        BeliefUpdateRequest(
            hypothesis_id=hypothesis.id,
            evidence_id=technical.id,
            interpretation=EvidenceInterpretation.TECHNICAL,
            rationale="Renderer failed before market exposure",
            evaluated_at=now,
        )
    )

    assert technical_result.update.applied is False
    assert technical_result.state.state_version == 1
    assert technical_result.state.confidence == 0.0
    assert technical_result.state.evidence_count == 0
    assert len(engine.list_state_history(hypothesis.id)) == 1

    stale = _record(
        evidence_class=EvidenceClass.MARKET,
        observed_at=now,
        kind="old_click",
    )
    _persist_and_bind(evidence_store, hypothesis, stale)
    stale_result = engine.apply(
        BeliefUpdateRequest(
            hypothesis_id=hypothesis.id,
            evidence_id=stale.id,
            interpretation=EvidenceInterpretation.SUPPORTING,
            rationale="Old click is outside TTL",
            evaluated_at=now + timedelta(seconds=61),
        )
    )

    assert stale_result.update.applied is False
    assert stale_result.update.freshness_weight == 0.0
    assert stale_result.state.state_version == 1
    assert len(engine.list_state_history(hypothesis.id)) == 1
    assert len(engine.list_updates(hypothesis.id)) == 2


def test_unbound_evidence_cannot_change_belief(postgres_dsn: str) -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.PRICING,
        subject="price acceptance",
        proposition="The market accepts the tested price",
    )
    PostgresBeliefStore(postgres_dsn).save_economic_hypothesis(hypothesis)

    evidence = _record(
        evidence_class=EvidenceClass.ECONOMIC,
        observed_at=now,
        kind="paid_order",
    )
    PostgresEvidenceStore(postgres_dsn).save_record(evidence)

    with pytest.raises(ValueError, match="not associated"):
        PostgresBeliefUpdateEngine(postgres_dsn).apply(
            BeliefUpdateRequest(
                hypothesis_id=hypothesis.id,
                evidence_id=evidence.id,
                interpretation=EvidenceInterpretation.SUPPORTING,
                rationale="Paid order supports price acceptance",
                evaluated_at=now,
            )
        )

    assert PostgresBeliefStore(postgres_dsn).get_belief_state(hypothesis.id) is None


def test_concurrent_evidence_updates_allocate_distinct_versions(postgres_dsn: str) -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    belief_store = PostgresBeliefStore(postgres_dsn)
    evidence_store = PostgresEvidenceStore(postgres_dsn)
    hypothesis = EconomicHypothesis(
        hypothesis_type=HypothesisType.CHANNEL,
        subject="channel response",
        proposition="The channel produces qualified market response",
    )
    belief_store.save_economic_hypothesis(hypothesis)

    first_evidence = _record(
        evidence_class=EvidenceClass.MARKET,
        observed_at=now,
        kind="concurrent_reply_a",
    )
    second_evidence = _record(
        evidence_class=EvidenceClass.MARKET,
        observed_at=now + timedelta(milliseconds=1),
        kind="concurrent_reply_b",
    )
    _persist_and_bind(evidence_store, hypothesis, first_evidence)
    _persist_and_bind(evidence_store, hypothesis, second_evidence)

    requests = [
        BeliefUpdateRequest(
            hypothesis_id=hypothesis.id,
            evidence_id=first_evidence.id,
            interpretation=EvidenceInterpretation.SUPPORTING,
            rationale="Concurrent observation A",
            evaluated_at=now + timedelta(seconds=1),
        ),
        BeliefUpdateRequest(
            hypothesis_id=hypothesis.id,
            evidence_id=second_evidence.id,
            interpretation=EvidenceInterpretation.SUPPORTING,
            rationale="Concurrent observation B",
            evaluated_at=now + timedelta(seconds=1),
        ),
    ]

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(PostgresBeliefUpdateEngine(postgres_dsn).apply, requests))

    assert {result.update.resulting_state_version for result in results} == {2, 3}
    history = PostgresBeliefUpdateEngine(postgres_dsn).list_state_history(hypothesis.id)
    assert [state.state_version for state in history] == [1, 2, 3]
    assert belief_store.get_belief_state(hypothesis.id) == history[-1]
    assert history[-1].evidence_count == 2
