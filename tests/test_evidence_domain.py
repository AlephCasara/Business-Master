from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from business_master.domain.enums import EvidenceClass, EvidenceProvenance
from business_master.domain.evidence import EvidenceRecord, EvidenceRef


def test_observed_evidence_is_explicitly_classified() -> None:
    subject_id = uuid4()
    record = EvidenceRecord(
        evidence_class=EvidenceClass.MARKET,
        provenance=EvidenceProvenance.OBSERVED_OFFICIAL_EXTERNAL,
        kind="metric_snapshot",
        source="youtube.analytics",
        independence_key="channel:finance-01",
        source_event_id="video-123:2026-10-07T00:00:00Z",
        subject_type="externalization",
        subject_id=subject_id,
        features={"views": 1000, "external_clicks": 4},
    )

    assert record.evidence_class is EvidenceClass.MARKET
    assert record.provenance is EvidenceProvenance.OBSERVED_OFFICIAL_EXTERNAL
    assert record.subject_id == subject_id
    assert record.independence_key == "channel:finance-01"
    assert record.input_evidence_ids == []


def test_evidence_independence_identity_must_be_explicit_and_trimmed() -> None:
    with pytest.raises(ValidationError, match="source identities must be trimmed"):
        EvidenceRecord(
            evidence_class=EvidenceClass.MARKET,
            provenance=EvidenceProvenance.OBSERVED_OWN,
            kind="reply",
            source="crm",
            independence_key=" company-a ",
        )


def test_derived_evidence_requires_explicit_lineage() -> None:
    with pytest.raises(ValidationError, match="requires input_evidence_ids"):
        EvidenceRecord(
            evidence_class=EvidenceClass.ECONOMIC,
            provenance=EvidenceProvenance.CALCULATED,
            kind="contribution",
            source="business_master.unit_economics",
            features={"contribution": 12.5},
        )

    parent_id = uuid4()
    derived = EvidenceRecord(
        evidence_class=EvidenceClass.ECONOMIC,
        provenance=EvidenceProvenance.CALCULATED,
        kind="contribution",
        source="business_master.unit_economics",
        features={"contribution": 12.5},
        input_evidence_ids=[parent_id],
    )
    assert derived.input_evidence_ids == [parent_id]


def test_observed_evidence_cannot_claim_derived_inputs() -> None:
    with pytest.raises(ValidationError, match="cannot declare derived inputs"):
        EvidenceRecord(
            evidence_class=EvidenceClass.MARKET,
            provenance=EvidenceProvenance.OBSERVED_OWN,
            kind="reply",
            source="crm",
            input_evidence_ids=[uuid4()],
        )


def test_evidence_rejects_ambiguous_subject_or_lineage() -> None:
    with pytest.raises(ValidationError, match="provided together"):
        EvidenceRecord(
            evidence_class=EvidenceClass.TECHNICAL,
            provenance=EvidenceProvenance.OBSERVED_OWN,
            kind="render_succeeded",
            source="executor",
            subject_type="execution",
        )

    record_id = uuid4()
    with pytest.raises(ValidationError, match="derive from itself"):
        EvidenceRecord(
            id=record_id,
            evidence_class=EvidenceClass.ECONOMIC,
            provenance=EvidenceProvenance.INFERRED,
            kind="estimated_ltv",
            source="model",
            input_evidence_ids=[record_id],
        )


def test_legacy_conversion_requires_explicit_semantics() -> None:
    legacy = EvidenceRef(
        kind="metric_snapshot",
        source="youtube",
        entity_id=uuid4(),
        features={"views": 10},
    )

    with pytest.raises(ValueError, match="subject_type is required"):
        EvidenceRecord.from_legacy(
            legacy,
            evidence_class=EvidenceClass.MARKET,
            provenance=EvidenceProvenance.OBSERVED_OFFICIAL_EXTERNAL,
        )

    converted = EvidenceRecord.from_legacy(
        legacy,
        evidence_class=EvidenceClass.MARKET,
        provenance=EvidenceProvenance.OBSERVED_OFFICIAL_EXTERNAL,
        subject_type="experiment",
    )
    assert converted.id == legacy.id
    assert converted.subject_id == legacy.entity_id
    assert converted.independence_key is None
