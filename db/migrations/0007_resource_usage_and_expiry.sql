BEGIN;

ALTER TABLE resource_reservation
    ADD COLUMN IF NOT EXISTS expires_at timestamptz,
    ADD COLUMN IF NOT EXISTS expired_at timestamptz;

ALTER TABLE resource_reservation
    ADD CONSTRAINT ck_resource_reservation_expiry_consistency CHECK (
        expired_at IS NULL
        OR (
            expires_at IS NOT NULL
            AND status = 'released'
            AND released_at IS NOT NULL
            AND released_at = expired_at
            AND expired_at >= expires_at
        )
    );

CREATE INDEX IF NOT EXISTS ix_resource_reservation_expiry
    ON resource_reservation (expires_at)
    WHERE status = 'active' AND expires_at IS NOT NULL;

CREATE TABLE IF NOT EXISTS resource_usage (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id uuid NOT NULL REFERENCES resource_reservation(id) ON DELETE RESTRICT,
    execution_id uuid,
    idempotency_key text NOT NULL UNIQUE CHECK (btrim(idempotency_key) <> ''),
    actual jsonb NOT NULL CHECK (
        jsonb_typeof(actual) = 'object'
        AND actual <> '{}'::jsonb
    ),
    observed_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_resource_usage_reservation
    ON resource_usage (reservation_id, observed_at DESC);

CREATE INDEX IF NOT EXISTS ix_resource_usage_execution
    ON resource_usage (execution_id, observed_at DESC)
    WHERE execution_id IS NOT NULL;

COMMIT;
