BEGIN;

CREATE TABLE IF NOT EXISTS action_intent (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key text NOT NULL UNIQUE,
    action_type text NOT NULL,
    entity_id uuid NOT NULL,
    reason text NOT NULL,
    priority integer NOT NULL DEFAULT 0,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    status text NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'dispatched', 'completed', 'cancelled')),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_action_intent_entity_type
    ON action_intent (entity_id, action_type, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_action_intent_pending
    ON action_intent (priority DESC, created_at ASC)
    WHERE status IN ('pending', 'dispatched');

COMMIT;
