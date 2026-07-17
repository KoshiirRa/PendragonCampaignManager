BEGIN;

CREATE TABLE dice_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    session_id uuid REFERENCES campaign_sessions(id) ON DELETE SET NULL,
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    roller_type text NOT NULL,
    roller_id uuid,
    expression text NOT NULL,
    individual_rolls smallint[] NOT NULL,
    modifier smallint NOT NULL DEFAULT 0,
    total integer NOT NULL,
    target_number smallint,
    outcome text,
    purpose text,
    rolled_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT dice_logs_expression_not_blank CHECK (btrim(expression) <> ''),
    CONSTRAINT dice_logs_rolls_present CHECK (cardinality(individual_rolls) > 0)
);

CREATE INDEX dice_logs_campaign_time_idx ON dice_logs(campaign_id, rolled_at);
CREATE INDEX dice_logs_session_idx ON dice_logs(session_id) WHERE session_id IS NOT NULL;

COMMIT;

