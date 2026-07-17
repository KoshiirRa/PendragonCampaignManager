BEGIN;

CREATE TABLE campaigns (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name citext NOT NULL,
    slug citext NOT NULL UNIQUE,
    description text,
    current_year smallint NOT NULL DEFAULT 485 CHECK (current_year BETWEEN 1 AND 9999),
    ruleset_version text NOT NULL DEFAULT 'Pendragon 6th Edition',
    timezone text NOT NULL DEFAULT 'UTC',
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    archived_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT campaigns_name_not_blank CHECK (btrim(name::text) <> ''),
    CONSTRAINT campaigns_slug_format CHECK (slug::text ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$')
);

CREATE TRIGGER campaigns_set_updated_at
BEFORE UPDATE ON campaigns
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE campaign_sessions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    session_number integer NOT NULL CHECK (session_number > 0),
    title text NOT NULL,
    summary text,
    played_at timestamptz,
    in_game_start_year smallint CHECK (in_game_start_year BETWEEN 1 AND 9999),
    in_game_end_year smallint CHECK (in_game_end_year BETWEEN 1 AND 9999),
    status text NOT NULL DEFAULT 'planned' CHECK (status IN ('planned', 'in_progress', 'completed', 'cancelled')),
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (campaign_id, session_number),
    CONSTRAINT sessions_title_not_blank CHECK (btrim(title) <> ''),
    CONSTRAINT sessions_year_order CHECK (in_game_end_year IS NULL OR in_game_start_year IS NULL OR in_game_end_year >= in_game_start_year)
);

CREATE INDEX campaign_sessions_campaign_idx ON campaign_sessions(campaign_id, session_number);
CREATE TRIGGER campaign_sessions_set_updated_at
BEFORE UPDATE ON campaign_sessions
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMIT;

