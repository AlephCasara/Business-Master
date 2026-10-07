BEGIN;

CREATE TABLE IF NOT EXISTS economic_ledger_transaction (
    id uuid PRIMARY KEY,
    idempotency_key text NOT NULL UNIQUE,
    occurred_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT now(),
    description text NOT NULL,
    experiment_id uuid REFERENCES experiment(id),
    offer_id uuid,
    channel_id uuid REFERENCES channel(id),
    external_ref text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS economic_ledger_posting (
    id uuid PRIMARY KEY,
    transaction_id uuid NOT NULL REFERENCES economic_ledger_transaction(id),
    account text NOT NULL CHECK (account IN (
        'cash',
        'accounts_receivable',
        'accounts_payable',
        'working_capital_asset',
        'revenue',
        'refunds_returns',
        'fees',
        'direct_costs',
        'acquisition_spend',
        'equity'
    )),
    side text NOT NULL CHECK (side IN ('debit', 'credit')),
    amount numeric(24, 6) NOT NULL CHECK (amount > 0),
    currency text NOT NULL CHECK (currency ~ '^[A-Z]{3}$')
);

CREATE INDEX IF NOT EXISTS ix_economic_ledger_transaction_occurred
    ON economic_ledger_transaction (occurred_at, id);
CREATE INDEX IF NOT EXISTS ix_economic_ledger_transaction_experiment
    ON economic_ledger_transaction (experiment_id, occurred_at)
    WHERE experiment_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_economic_ledger_transaction_offer
    ON economic_ledger_transaction (offer_id, occurred_at)
    WHERE offer_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_economic_ledger_transaction_channel
    ON economic_ledger_transaction (channel_id, occurred_at)
    WHERE channel_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_economic_ledger_posting_account_currency
    ON economic_ledger_posting (account, currency, transaction_id);

COMMIT;
