BEGIN;

ALTER TABLE evidence_record
    ADD COLUMN IF NOT EXISTS independence_key text;

ALTER TABLE evidence_record
    DROP CONSTRAINT IF EXISTS ck_evidence_record_independence_key_trimmed;

ALTER TABLE evidence_record
    ADD CONSTRAINT ck_evidence_record_independence_key_trimmed
    CHECK (
        independence_key IS NULL
        OR (
            length(independence_key) BETWEEN 1 AND 255
            AND independence_key = btrim(independence_key)
        )
    );

CREATE INDEX IF NOT EXISTS ix_evidence_record_independence_key
    ON evidence_record (independence_key)
    WHERE independence_key IS NOT NULL;

COMMIT;
