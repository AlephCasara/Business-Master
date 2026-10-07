BEGIN;

CREATE TABLE IF NOT EXISTS experiment_contract (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    economic_hypothesis_id uuid NOT NULL REFERENCES economic_hypothesis(id) ON DELETE RESTRICT,
    business_family text NOT NULL CHECK (btrim(business_family) <> ''),
    question text NOT NULL CHECK (btrim(question) <> ''),
    intervention_dimensions jsonb NOT NULL DEFAULT '{}'::jsonb,
    held_constant_dimensions text[] NOT NULL DEFAULT '{}',
    expected_observation text NOT NULL CHECK (btrim(expected_observation) <> ''),
    falsification_condition text NOT NULL CHECK (btrim(falsification_condition) <> ''),
    measurement jsonb NOT NULL,
    budget jsonb NOT NULL,
    parent_contract_id uuid REFERENCES experiment_contract(id) ON DELETE RESTRICT,
    supersedes_contract_id uuid REFERENCES experiment_contract(id) ON DELETE RESTRICT,
    origin_decision_id uuid REFERENCES decision(id) ON DELETE RESTRICT,
    contract_version integer NOT NULL DEFAULT 1 CHECK (contract_version >= 1),
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (parent_contract_id IS NULL OR parent_contract_id <> id),
    CHECK (supersedes_contract_id IS NULL OR supersedes_contract_id <> id)
);

CREATE TABLE IF NOT EXISTS experiment_contract_binding (
    experiment_id uuid PRIMARY KEY REFERENCES experiment(id) ON DELETE CASCADE,
    contract_id uuid NOT NULL UNIQUE REFERENCES experiment_contract(id) ON DELETE RESTRICT,
    bound_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_experiment_contract_hypothesis
    ON experiment_contract (economic_hypothesis_id, created_at);

CREATE INDEX IF NOT EXISTS idx_experiment_contract_parent
    ON experiment_contract (parent_contract_id)
    WHERE parent_contract_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_experiment_contract_supersedes
    ON experiment_contract (supersedes_contract_id)
    WHERE supersedes_contract_id IS NOT NULL;

COMMIT;
