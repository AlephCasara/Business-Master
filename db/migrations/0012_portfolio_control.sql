BEGIN;

CREATE TABLE IF NOT EXISTS portfolio_plan (
    id uuid PRIMARY KEY,
    idempotency_key text NOT NULL UNIQUE,
    policy_name text NOT NULL,
    policy_version text NOT NULL,
    base_currency char(3) NOT NULL,
    policy_parameters jsonb NOT NULL,
    available_resources jsonb NOT NULL,
    evaluations jsonb NOT NULL,
    created_at timestamptz NOT NULL
);

CREATE TABLE IF NOT EXISTS portfolio_allocation (
    id uuid PRIMARY KEY,
    plan_id uuid NOT NULL REFERENCES portfolio_plan(id) ON DELETE RESTRICT,
    candidate_id uuid NOT NULL,
    family_evaluation_id uuid NOT NULL REFERENCES family_evaluation(id) ON DELETE RESTRICT,
    hypothesis_id uuid NOT NULL REFERENCES economic_hypothesis(id) ON DELETE RESTRICT,
    contract_id uuid NOT NULL REFERENCES experiment_contract(id) ON DELETE RESTRICT,
    belief_state_version bigint NOT NULL CHECK (belief_state_version >= 1),
    current_tier text NOT NULL CHECK (current_tier IN ('probe', 'pilot', 'scale', 'paused', 'killed')),
    recommendation text NOT NULL CHECK (
        recommendation IN (
            'insufficient_evidence', 'continue', 'replicate',
            'graduate', 'pause', 'reject'
        )
    ),
    roles jsonb NOT NULL,
    group_key text NOT NULL,
    resource_demand jsonb NOT NULL,
    value_estimate jsonb NOT NULL,
    risk_assessment jsonb NOT NULL,
    capital_amount numeric(24,6),
    capital_currency char(3),
    capital_category text CHECK (
        capital_category IS NULL OR capital_category IN (
            'paid_ads', 'external_ai_api', 'cloud_gpu',
            'paid_saas', 'working_capital', 'other'
        )
    ),
    utility double precision NOT NULL,
    scarcity_pressure double precision NOT NULL CHECK (scarcity_pressure >= 0),
    rationale text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (plan_id, candidate_id),
    CHECK (
        (capital_amount IS NULL AND capital_currency IS NULL AND capital_category IS NULL)
        OR
        (capital_amount IS NOT NULL AND capital_amount > 0
         AND capital_currency IS NOT NULL AND capital_category IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS ix_portfolio_allocation_hypothesis
    ON portfolio_allocation (hypothesis_id, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_portfolio_allocation_family_evaluation
    ON portfolio_allocation (family_evaluation_id);

COMMIT;
