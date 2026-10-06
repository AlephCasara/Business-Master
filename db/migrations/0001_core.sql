BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS hypothesis (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    thesis text NOT NULL,
    family text NOT NULL,
    market text,
    audience text,
    tier text NOT NULL DEFAULT 'probe'
        CHECK (tier IN ('probe', 'pilot', 'scale', 'paused', 'killed')),
    parent_id uuid REFERENCES hypothesis(id),
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS channel (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    platform text NOT NULL,
    external_id text,
    name text NOT NULL,
    account_id uuid,
    language text,
    geography text,
    status text NOT NULL DEFAULT 'bootstrap',
    editorial_profile jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (platform, external_id)
);

CREATE TABLE IF NOT EXISTS experiment (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    hypothesis_id uuid NOT NULL REFERENCES hypothesis(id),
    parent_id uuid REFERENCES experiment(id),
    status text NOT NULL DEFAULT 'planned'
        CHECK (status IN (
            'planned', 'queued', 'running', 'waiting_external', 'waiting_human',
            'measuring', 'complete', 'failed', 'cancelled'
        )),
    tier text NOT NULL DEFAULT 'probe'
        CHECK (tier IN ('probe', 'pilot', 'scale', 'paused', 'killed')),
    business_family text NOT NULL,
    channel_id uuid REFERENCES channel(id),
    product_id uuid,
    mutation jsonb,
    dimensions jsonb NOT NULL DEFAULT '{}'::jsonb,
    expected_cash_cost numeric(18, 6) NOT NULL DEFAULT 0,
    expected_compute_units double precision NOT NULL DEFAULT 0,
    expected_human_minutes double precision NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL DEFAULT now(),
    started_at timestamptz,
    completed_at timestamptz
);

CREATE TABLE IF NOT EXISTS creative (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id uuid NOT NULL REFERENCES experiment(id),
    parent_id uuid REFERENCES creative(id),
    kind text NOT NULL,
    concept jsonb NOT NULL DEFAULT '{}'::jsonb,
    generation_spec jsonb NOT NULL DEFAULT '{}'::jsonb,
    status text NOT NULL DEFAULT 'planned',
    created_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz
);

CREATE TABLE IF NOT EXISTS asset (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    creative_id uuid REFERENCES creative(id),
    experiment_id uuid REFERENCES experiment(id),
    kind text NOT NULL,
    uri text NOT NULL,
    sha256 text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS evidence (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    kind text NOT NULL,
    source text NOT NULL,
    entity_id uuid,
    observed_at timestamptz NOT NULL DEFAULT now(),
    features jsonb NOT NULL DEFAULT '{}'::jsonb,
    payload_ref text
);

CREATE TABLE IF NOT EXISTS hypothesis_evidence (
    hypothesis_id uuid NOT NULL REFERENCES hypothesis(id) ON DELETE CASCADE,
    evidence_id uuid NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    PRIMARY KEY (hypothesis_id, evidence_id)
);

CREATE TABLE IF NOT EXISTS experiment_evidence (
    experiment_id uuid NOT NULL REFERENCES experiment(id) ON DELETE CASCADE,
    evidence_id uuid NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    PRIMARY KEY (experiment_id, evidence_id)
);

CREATE TABLE IF NOT EXISTS metric_snapshot (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id uuid NOT NULL REFERENCES experiment(id) ON DELETE CASCADE,
    observed_at timestamptz NOT NULL DEFAULT now(),
    age_seconds integer NOT NULL DEFAULT 0,
    metrics jsonb NOT NULL DEFAULT '{}'::jsonb,
    source text NOT NULL,
    external boolean NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS business_outcome (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id uuid NOT NULL REFERENCES experiment(id) ON DELETE CASCADE,
    observed_at timestamptz NOT NULL DEFAULT now(),
    revenue numeric(18, 6) NOT NULL DEFAULT 0,
    gross_profit numeric(18, 6),
    currency text NOT NULL DEFAULT 'USD',
    orders integer NOT NULL DEFAULT 0,
    leads integer NOT NULL DEFAULT 0,
    clicks integer NOT NULL DEFAULT 0,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS decision (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id uuid NOT NULL,
    decision_type text NOT NULL,
    policy_name text NOT NULL,
    policy_version text NOT NULL,
    evidence_ids uuid[] NOT NULL DEFAULT '{}',
    observed_features jsonb NOT NULL DEFAULT '{}'::jsonb,
    chosen_action jsonb NOT NULL DEFAULT '{}'::jsonb,
    expected_value double precision,
    expected_cash_cost numeric(18, 6) NOT NULL DEFAULT 0,
    expected_compute_units double precision NOT NULL DEFAULT 0,
    expected_human_minutes double precision NOT NULL DEFAULT 0,
    risk text NOT NULL DEFAULT 'low'
        CHECK (risk IN ('zero', 'low', 'medium', 'high', 'critical')),
    rationale text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS resource (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL UNIQUE,
    kind text NOT NULL,
    available boolean NOT NULL DEFAULT true,
    capacity double precision NOT NULL DEFAULT 1,
    labels jsonb NOT NULL DEFAULT '{}'::jsonb,
    last_seen_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS execution (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id uuid REFERENCES experiment(id),
    success boolean NOT NULL,
    signal_kind text NOT NULL,
    started_at timestamptz NOT NULL,
    completed_at timestamptz NOT NULL DEFAULT now(),
    wall_seconds double precision NOT NULL DEFAULT 0,
    cpu_seconds double precision,
    gpu_seconds double precision,
    model_tokens bigint,
    retries integer NOT NULL DEFAULT 0,
    human_minutes double precision NOT NULL DEFAULT 0,
    cash_cost numeric(18, 6) NOT NULL DEFAULT 0,
    error_code text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS human_action_request (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    action_type text NOT NULL,
    reason text NOT NULL,
    experiment_id uuid REFERENCES experiment(id),
    account_id uuid,
    risk text NOT NULL DEFAULT 'high'
        CHECK (risk IN ('zero', 'low', 'medium', 'high', 'critical')),
    required_by timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    resolved_at timestamptz
);

CREATE TABLE IF NOT EXISTS domain_event (
    sequence_id bigserial PRIMARY KEY,
    id uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    name text NOT NULL,
    aggregate_type text NOT NULL,
    aggregate_id uuid NOT NULL,
    occurred_at timestamptz NOT NULL DEFAULT now(),
    causation_id uuid,
    correlation_id uuid NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    schema_version integer NOT NULL DEFAULT 1,
    processed_at timestamptz
);

CREATE INDEX IF NOT EXISTS ix_hypothesis_tier_active
    ON hypothesis (tier, active);
CREATE INDEX IF NOT EXISTS ix_experiment_hypothesis_status
    ON experiment (hypothesis_id, status);
CREATE INDEX IF NOT EXISTS ix_experiment_channel_created
    ON experiment (channel_id, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_metric_experiment_observed
    ON metric_snapshot (experiment_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS ix_outcome_experiment_observed
    ON business_outcome (experiment_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS ix_evidence_entity_observed
    ON evidence (entity_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS ix_event_unprocessed
    ON domain_event (sequence_id)
    WHERE processed_at IS NULL;
CREATE INDEX IF NOT EXISTS ix_human_action_open
    ON human_action_request (created_at)
    WHERE resolved_at IS NULL;

COMMIT;
