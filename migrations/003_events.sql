BEGIN;

CREATE TYPE event_visibility AS ENUM ('gm_only', 'players', 'public');

CREATE TABLE events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    session_id uuid REFERENCES campaign_sessions(id) ON DELETE SET NULL,
    event_type text NOT NULL,
    title text NOT NULL,
    description text,
    in_game_year smallint NOT NULL CHECK (in_game_year BETWEEN 1 AND 9999),
    in_game_date text,
    sequence integer NOT NULL DEFAULT 0 CHECK (sequence >= 0),
    visibility event_visibility NOT NULL DEFAULT 'players',
    occurred_at timestamptz,
    recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    supersedes_event_id uuid REFERENCES events(id) ON DELETE RESTRICT,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT events_type_not_blank CHECK (btrim(event_type) <> ''),
    CONSTRAINT events_title_not_blank CHECK (btrim(title) <> ''),
    CONSTRAINT events_not_self_superseding CHECK (supersedes_event_id IS NULL OR supersedes_event_id <> id)
);

CREATE INDEX events_timeline_idx ON events(campaign_id, in_game_year, sequence, recorded_at);
CREATE INDEX events_type_idx ON events(campaign_id, event_type);
CREATE INDEX events_session_idx ON events(session_id) WHERE session_id IS NOT NULL;

CREATE TABLE event_links (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id uuid NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    entity_type text NOT NULL,
    entity_id uuid NOT NULL,
    role text NOT NULL DEFAULT 'subject',
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (event_id, entity_type, entity_id, role),
    CONSTRAINT event_links_entity_type_not_blank CHECK (btrim(entity_type) <> ''),
    CONSTRAINT event_links_role_not_blank CHECK (btrim(role) <> '')
);

CREATE INDEX event_links_entity_idx ON event_links(entity_type, entity_id);

COMMIT;

