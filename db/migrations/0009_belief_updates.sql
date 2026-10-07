BEGIN;

CREATE TABLE IF NOT EXISTS belief_state_version (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    hypothesis_id uuid NOT NULL
        REFERENCES economic_hypothesis(id) ON DELETE CASCADE,
    state_version bigint NOT NULL CHECK (state_version >= 1),
    confidence double precision NOT NULL
        CHECK (confidence >= 0 AND confidence <= 1),
    uncertainty double precision NOT NULL
        CHECK (uncertainty >= 0 AND uncertainty <= 1),
    evidence_count integer NOT NULL CHECK (evidence_count >= 0),
    valid_from timestamptz NOT NULL,
    last_evidence_at timestamptz,
    freshness double precision NOT NULL
        CHECK (freshness >= 0 AND freshness <= 1),
    updated_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (hypothesis_id, state_version)
);

INSERT INTO belief_state_version (
    hypothesis_id,
    state_version,
    confidence,
    uncertainty,
    evidence_count,
    valid_from,
    last_evidence_at,
    freshness,
    updated_at
)
SELECT
    hypothesis_id,
    state_version,
    confidence,
    uncertainty,
    evidence_count,
    valid_from,
    last_evidence_at,
    freshness,
    updated_at
FROM belief_state
ON CONFLICT (hypothesis_id, state_version) DO NOTHING;

CREATE TABLE IF NOT EXISTS belief_update (
    id uuid PRIMARY KEY,
    hypothesis_id uuid NOT NULL
        REFERENCES economic_hypothesis(id) ON DELETE RESTRICT,
    evidence_id uuid NOT NULL
        REFERENCES evidence_record(id) ON DELETE RESTRICT,
    interpretation text NOT NULL
        CHECK (interpretation IN ('supporting', 'falsifying', 'neutral', 'technical')),
    strength double precision NOT NULL
        CHECK (strength > 0 AND strength <= 1),
    interpretation_rationale text NOT NULL,
    policy_name text NOT NULL,
    policy_version text NOT NULL,
    evidence_class text NOT NULL
        CHECK (evidence_class IN ('technical', 'market', 'economic')),
    freshness_weight double precision NOT NULL
        CHECK (freshness_weight >= 0 AND freshness_weight <= 1),
    effective_weight double precision NOT NULL
        CHECK (effective_weight >= 0 AND effective_weight <= 1),
    prior_state_version bigint NOT NULL CHECK (prior_state_version >= 1),
    resulting_state_version bigint NOT NULL CHECK (resulting_state_version >= 1),
    confidence_before double precision NOT NULL
        CHECK (confidence_before >= 0 AND confidence_before <= 1),
    confidence_after double precision NOT NULL
        CHECK (confidence_after >= 0 AND confidence_after <= 1),
    uncertainty_before double precision NOT NULL
        CHECK (uncertainty_before >= 0 AND uncertainty_before <= 1),
    uncertainty_after double precision NOT NULL
        CHECK (uncertainty_after >= 0 AND uncertainty_after <= 1),
    evidence_count_before integer NOT NULL CHECK (evidence_count_before >= 0),
    evidence_count_after integer NOT NULL CHECK (evidence_count_after >= 0),
    applied boolean NOT NULL,
    policy_rationale text NOT NULL,
    evaluated_at timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (hypothesis_id, evidence_id)
);

CREATE INDEX IF NOT EXISTS ix_belief_state_version_hypothesis
    ON belief_state_version (hypothesis_id, state_version DESC);

CREATE INDEX IF NOT EXISTS ix_belief_update_hypothesis_created
    ON belief_update (hypothesis_id, created_at ASC, id ASC);

CREATE INDEX IF NOT EXISTS ix_belief_update_evidence
    ON belief_update (evidence_id);

COMMIT;
