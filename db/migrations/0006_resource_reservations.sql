BEGIN;

ALTER TABLE resource
    ALTER COLUMN capacity TYPE numeric(24, 6)
    USING capacity::numeric;

ALTER TABLE resource
    DROP CONSTRAINT IF EXISTS ck_resource_capacity_nonnegative;
ALTER TABLE resource
    ADD CONSTRAINT ck_resource_capacity_nonnegative CHECK (capacity >= 0);

ALTER TABLE experiment_contract
    ADD COLUMN IF NOT EXISTS resource_requirements jsonb NOT NULL DEFAULT '{}'::jsonb;

CREATE TABLE IF NOT EXISTS resource_reservation (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_type text NOT NULL CHECK (btrim(owner_type) <> ''),
    owner_id uuid NOT NULL,
    idempotency_key text NOT NULL UNIQUE CHECK (btrim(idempotency_key) <> ''),
    requirements jsonb NOT NULL CHECK (jsonb_typeof(requirements) = 'object'),
    status text NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'released')),
    created_at timestamptz NOT NULL DEFAULT now(),
    released_at timestamptz,
    CHECK (
        (status = 'active' AND released_at IS NULL)
        OR (status = 'released' AND released_at IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS resource_reservation_item (
    reservation_id uuid NOT NULL REFERENCES resource_reservation(id) ON DELETE CASCADE,
    resource_id uuid NOT NULL REFERENCES resource(id) ON DELETE RESTRICT,
    amount numeric(24, 6) NOT NULL CHECK (amount > 0),
    PRIMARY KEY (reservation_id, resource_id)
);

CREATE INDEX IF NOT EXISTS ix_resource_reservation_owner
    ON resource_reservation (owner_type, owner_id, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_resource_reservation_active
    ON resource_reservation (created_at)
    WHERE status = 'active';

CREATE INDEX IF NOT EXISTS ix_resource_reservation_item_resource
    ON resource_reservation_item (resource_id, reservation_id);

COMMIT;
