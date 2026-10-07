BEGIN;

ALTER TABLE decision
    ADD COLUMN IF NOT EXISTS idempotency_key text,
    ADD COLUMN IF NOT EXISTS parent_experiment_id uuid REFERENCES experiment(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS portfolio_allocation_id uuid REFERENCES portfolio_allocation(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS family_evaluation_id uuid REFERENCES family_evaluation(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS hypothesis_id uuid REFERENCES economic_hypothesis(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS source_contract_id uuid REFERENCES experiment_contract(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS belief_state_version bigint,
    ADD COLUMN IF NOT EXISTS continuation_kind text,
    ADD COLUMN IF NOT EXISTS target_tier text,
    ADD COLUMN IF NOT EXISTS expected_resource_demand jsonb,
    ADD COLUMN IF NOT EXISTS capital_requirement jsonb,
    ADD COLUMN IF NOT EXISTS blast_radius double precision,
    ADD COLUMN IF NOT EXISTS reversible boolean,
    ADD COLUMN IF NOT EXISTS human_gate_required boolean,
    ADD COLUMN IF NOT EXISTS reservation_expires_at timestamptz,
    ADD COLUMN IF NOT EXISTS child_experiment_id uuid REFERENCES experiment(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS child_contract_id uuid REFERENCES experiment_contract(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS resource_reservation_id uuid REFERENCES resource_reservation(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS capital_authorization_id uuid REFERENCES capital_authorization(id) ON DELETE RESTRICT;

ALTER TABLE decision
    ADD CONSTRAINT ck_decision_v2_idempotency_trimmed CHECK (
        idempotency_key IS NULL OR (btrim(idempotency_key) <> '' AND idempotency_key = btrim(idempotency_key))
    ),
    ADD CONSTRAINT ck_decision_v2_belief_version CHECK (
        belief_state_version IS NULL OR belief_state_version >= 1
    ),
    ADD CONSTRAINT ck_decision_v2_continuation_kind CHECK (
        continuation_kind IS NULL OR continuation_kind IN ('none', 'replicate', 'graduate')
    ),
    ADD CONSTRAINT ck_decision_v2_target_tier CHECK (
        target_tier IS NULL OR target_tier IN ('probe', 'pilot', 'scale')
    ),
    ADD CONSTRAINT ck_decision_v2_resource_vector CHECK (
        expected_resource_demand IS NULL OR jsonb_typeof(expected_resource_demand) = 'object'
    ),
    ADD CONSTRAINT ck_decision_v2_capital_requirement CHECK (
        capital_requirement IS NULL OR jsonb_typeof(capital_requirement) = 'object'
    ),
    ADD CONSTRAINT ck_decision_v2_blast_radius CHECK (
        blast_radius IS NULL OR (blast_radius >= 0 AND blast_radius <= 1)
    ),
    ADD CONSTRAINT ck_decision_v2_child_pair CHECK (
        (child_experiment_id IS NULL AND child_contract_id IS NULL)
        OR (child_experiment_id IS NOT NULL AND child_contract_id IS NOT NULL)
    );

CREATE UNIQUE INDEX IF NOT EXISTS ux_decision_v2_idempotency
    ON decision (idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS ux_decision_v2_portfolio_allocation
    ON decision (portfolio_allocation_id)
    WHERE portfolio_allocation_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS ux_decision_v2_child_experiment
    ON decision (child_experiment_id)
    WHERE child_experiment_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS ux_decision_v2_child_contract
    ON decision (child_contract_id)
    WHERE child_contract_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_decision_v2_hypothesis_created
    ON decision (hypothesis_id, created_at DESC)
    WHERE hypothesis_id IS NOT NULL;

COMMIT;
