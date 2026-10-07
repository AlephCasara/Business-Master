BEGIN;

CREATE TABLE IF NOT EXISTS capital_authorization (
    id uuid PRIMARY KEY,
    idempotency_key text NOT NULL UNIQUE,
    portfolio_allocation_id uuid NOT NULL REFERENCES portfolio_allocation(id) ON DELETE RESTRICT,
    family_evaluation_id uuid NOT NULL REFERENCES family_evaluation(id) ON DELETE RESTRICT,
    hypothesis_id uuid NOT NULL REFERENCES economic_hypothesis(id) ON DELETE RESTRICT,
    amount numeric(24,6) NOT NULL CHECK (amount > 0),
    currency char(3) NOT NULL,
    category text NOT NULL CHECK (
        category IN (
            'paid_ads', 'external_ai_api', 'cloud_gpu',
            'paid_saas', 'working_capital', 'other'
        )
    ),
    stage text NOT NULL CHECK (stage IN ('locked', 'probe', 'validated', 'pilot', 'scale')),
    risk text NOT NULL CHECK (risk IN ('zero', 'low', 'medium', 'high', 'critical')),
    policy_name text NOT NULL,
    policy_version text NOT NULL,
    envelope jsonb NOT NULL,
    ledger_cash_at_authorization numeric(24,6) NOT NULL,
    active_outstanding_before numeric(24,6) NOT NULL CHECK (active_outstanding_before >= 0),
    period_committed_before numeric(24,6) NOT NULL CHECK (period_committed_before >= 0),
    status text NOT NULL CHECK (status IN ('active', 'consumed', 'released', 'expired')),
    rationale text NOT NULL,
    authorized_at timestamptz NOT NULL,
    expires_at timestamptz,
    consumed_at timestamptz,
    released_at timestamptz,
    expired_at timestamptz,
    ledger_transaction_id uuid REFERENCES economic_ledger_transaction(id) ON DELETE RESTRICT,
    CHECK (
        (status = 'active' AND consumed_at IS NULL AND released_at IS NULL
         AND expired_at IS NULL AND ledger_transaction_id IS NULL)
        OR
        (status = 'consumed' AND consumed_at IS NOT NULL AND ledger_transaction_id IS NOT NULL)
        OR
        (status = 'released' AND released_at IS NOT NULL AND expired_at IS NULL)
        OR
        (status = 'expired' AND released_at IS NOT NULL AND expired_at IS NOT NULL
         AND released_at = expired_at)
    )
);

CREATE INDEX IF NOT EXISTS ix_capital_authorization_active_currency
    ON capital_authorization (currency, status)
    WHERE status = 'active';

CREATE INDEX IF NOT EXISTS ix_capital_authorization_category_period
    ON capital_authorization (currency, category, authorized_at, status);

CREATE INDEX IF NOT EXISTS ix_capital_authorization_allocation
    ON capital_authorization (portfolio_allocation_id);

COMMIT;
