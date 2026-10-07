BEGIN;

CREATE TABLE IF NOT EXISTS evidence_record (
    id uuid PRIMARY KEY,
    evidence_class text NOT NULL
        CHECK (evidence_class IN ('technical', 'market', 'economic')),
    provenance text NOT NULL
        CHECK (provenance IN (
            'observed_own',
            'observed_official_external',
            'observed_public',
            'calculated',
            'inferred',
            'creator_claim',
            'unknown'
        )),
    kind text NOT NULL,
    source text NOT NULL,
    source_event_id text,
    subject_type text,
    subject_id uuid,
    observed_at timestamptz NOT NULL,
    ingested_at timestamptz NOT NULL,
    features jsonb NOT NULL DEFAULT '{}'::jsonb,
    payload_ref text,
    schema_version integer NOT NULL DEFAULT 1
        CHECK (schema_version >= 1),
    CHECK (
        (subject_type IS NULL AND subject_id IS NULL)
        OR (subject_type IS NOT NULL AND subject_id IS NOT NULL)
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_evidence_record_source_event
    ON evidence_record (source, source_event_id)
    WHERE source_event_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_evidence_record_subject_observed
    ON evidence_record (subject_type, subject_id, observed_at DESC);

CREATE INDEX IF NOT EXISTS ix_evidence_record_class_observed
    ON evidence_record (evidence_class, observed_at DESC);

CREATE TABLE IF NOT EXISTS evidence_input (
    evidence_id uuid NOT NULL
        REFERENCES evidence_record(id) ON DELETE RESTRICT,
    input_evidence_id uuid NOT NULL
        REFERENCES evidence_record(id) ON DELETE RESTRICT,
    ordinal integer NOT NULL CHECK (ordinal >= 0),
    PRIMARY KEY (evidence_id, input_evidence_id),
    UNIQUE (evidence_id, ordinal),
    CHECK (evidence_id <> input_evidence_id)
);

CREATE TABLE IF NOT EXISTS evidence_association (
    evidence_id uuid NOT NULL
        REFERENCES evidence_record(id) ON DELETE RESTRICT,
    target_kind text NOT NULL
        CHECK (target_kind IN (
            'economic_hypothesis',
            'experiment_contract',
            'experiment'
        )),
    target_id uuid NOT NULL,
    linked_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (evidence_id, target_kind, target_id)
);

CREATE INDEX IF NOT EXISTS ix_evidence_association_target
    ON evidence_association (target_kind, target_id, evidence_id);

COMMIT;
