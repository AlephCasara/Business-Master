BEGIN;

CREATE TABLE IF NOT EXISTS family_evaluation (
    id uuid PRIMARY KEY,
    idempotency_key text NOT NULL UNIQUE,
    family text NOT NULL CHECK (family IN ('content', 'b2b', 'commerce', 'capability')),
    hypothesis_id uuid NOT NULL REFERENCES economic_hypothesis(id) ON DELETE RESTRICT,
    contract_id uuid NOT NULL REFERENCES experiment_contract(id) ON DELETE RESTRICT,
    belief_state_version bigint NOT NULL CHECK (belief_state_version >= 1),
    current_tier text NOT NULL CHECK (current_tier IN ('probe', 'pilot', 'scale', 'paused', 'killed')),
    policy_name text NOT NULL,
    policy_version text NOT NULL,
    evidence_ids jsonb NOT NULL DEFAULT '[]'::jsonb,
    interpretations jsonb NOT NULL DEFAULT '[]'::jsonb,
    criteria jsonb NOT NULL DEFAULT '[]'::jsonb,
    external_observations integer NOT NULL CHECK (external_observations >= 0),
    independent_sources integer NOT NULL CHECK (independent_sources >= 0),
    replication_count integer NOT NULL CHECK (replication_count >= 0),
    distinct_contexts integer NOT NULL CHECK (distinct_contexts >= 0),
    evidence_sufficient boolean NOT NULL,
    supporting_signal boolean NOT NULL,
    falsified boolean NOT NULL,
    economic_readiness text NOT NULL CHECK (
        economic_readiness IN ('unknown', 'not_ready', 'ready')
    ),
    operational_readiness text NOT NULL CHECK (
        operational_readiness IN ('unknown', 'not_ready', 'ready')
    ),
    recommendation text NOT NULL CHECK (
        recommendation IN (
            'insufficient_evidence', 'continue', 'replicate',
            'graduate', 'pause', 'reject'
        )
    ),
    rationale text NOT NULL,
    evaluated_at timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_family_evaluation_hypothesis_time
    ON family_evaluation (hypothesis_id, evaluated_at DESC);

CREATE INDEX IF NOT EXISTS ix_family_evaluation_contract_time
    ON family_evaluation (contract_id, evaluated_at DESC);

COMMIT;
