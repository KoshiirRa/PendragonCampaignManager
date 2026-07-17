BEGIN;

CREATE TABLE glory_ledger (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    session_id uuid REFERENCES campaign_sessions(id) ON DELETE SET NULL,
    awarded_year smallint NOT NULL CHECK (awarded_year BETWEEN 1 AND 9999),
    sequence integer NOT NULL DEFAULT 0 CHECK (sequence >= 0),
    amount integer NOT NULL CHECK (amount <> 0),
    category text NOT NULL DEFAULT 'other',
    reason text NOT NULL,
    scope knowledge_scope NOT NULL DEFAULT 'players',
    recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT glory_ledger_category_not_blank CHECK (btrim(category) <> ''),
    CONSTRAINT glory_ledger_reason_not_blank CHECK (btrim(reason) <> '')
);

CREATE INDEX glory_ledger_character_timeline_idx
    ON glory_ledger(character_id, awarded_year, sequence, recorded_at);
CREATE INDEX glory_ledger_campaign_year_idx
    ON glory_ledger(campaign_id, awarded_year, recorded_at);

COMMIT;

