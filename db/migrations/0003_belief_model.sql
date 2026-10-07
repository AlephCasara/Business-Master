BEGIN;

CREATE TABLE IF NOT EXISTS economic_hypothesis (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    hypothesis_type text NOT NULL CHECK (hypothesis_type IN (
        'demand', 'pain', 'audience', 'angle', 'hook', 'creative', 'offer',
        'pricing', 'acquisition', 'channel', 'funnel', 'aov', 'ltv', 'product',
        'supply', 'fulfillment', 'b2b_pain', 'outreach', 'delivery', 'capability',
        'asset'
    )),
    subject text NOT NULL,
    proposition text NOT NULL,
    mechanism text,
    context jsonb NOT NULL DEFAULT '{}'::jsonb,
    expected_observation text,
    falsification_condition text,
    evidence_requirements jsonb NOT NULL DEFAULT '{}'::jsonb,
    measurement_window_seconds bigint CHECK (
        measurement_window_seconds IS NULL OR measurement_window_seconds > 0
    ),
    freshness_policy jsonb NOT NULL DEFAULT '{"mode":"none"}'::jsonb,
    legacy_hypothesis_id uuid UNIQUE REFERENCES hypothesis(id),
    status text NOT NULL DEFAULT 'active'
        CHECK (status IN ('draft', 'active', 'paused', 'rejected', 'superseded')),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS economic_hypothesis_parent (
    hypothesis_id uuid NOT NULL REFERENCES economic_hypothesis(id) ON DELETE CASCADE,
    parent_id uuid NOT NULL REFERENCES economic_hypothesis(id) ON DELETE RESTRICT,
    PRIMARY KEY (hypothesis_id, parent_id),
    CHECK (hypothesis_id <> parent_id)
);

CREATE TABLE IF NOT EXISTS economic_hypothesis_dependency (
    hypothesis_id uuid NOT NULL REFERENCES economic_hypothesis(id) ON DELETE CASCADE,
    dependency_id uuid NOT NULL REFERENCES economic_hypothesis(id) ON DELETE RESTRICT,
    PRIMARY KEY (hypothesis_id, dependency_id),
    CHECK (hypothesis_id <> dependency_id)
);

CREATE TABLE IF NOT EXISTS belief_state (
    hypothesis_id uuid PRIMARY KEY REFERENCES economic_hypothesis(id) ON DELETE CASCADE,
    confidence double precision NOT NULL DEFAULT 0
        CHECK (confidence >= 0 AND confidence <= 1),
    uncertainty double precision NOT NULL DEFAULT 1
        CHECK (uncertainty >= 0 AND uncertainty <= 1),
    evidence_count integer NOT NULL DEFAULT 0 CHECK (evidence_count >= 0),
    valid_from timestamptz NOT NULL DEFAULT now(),
    last_evidence_at timestamptz,
    freshness double precision NOT NULL DEFAULT 1
        CHECK (freshness >= 0 AND freshness <= 1),
    state_version bigint NOT NULL DEFAULT 1 CHECK (state_version >= 1),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_economic_hypothesis_status_type
    ON economic_hypothesis (status, hypothesis_type);

CREATE INDEX IF NOT EXISTS idx_economic_hypothesis_parent_parent
    ON economic_hypothesis_parent (parent_id);

CREATE INDEX IF NOT EXISTS idx_economic_hypothesis_dependency_dependency
    ON economic_hypothesis_dependency (dependency_id);

COMMIT;
