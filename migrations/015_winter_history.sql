BEGIN;

CREATE TABLE character_history_entries (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    event_id uuid NOT NULL REFERENCES events(id) ON DELETE RESTRICT,
    source_key text NOT NULL,
    in_game_year smallint NOT NULL CHECK (in_game_year BETWEEN 1 AND 9999),
    title text NOT NULL CHECK (btrim(title) <> ''),
    source text,
    description text,
    reported_glory integer NOT NULL DEFAULT 0,
    favour_value integer NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (campaign_id, source_key)
);
CREATE INDEX character_history_timeline_idx ON character_history_entries(character_id, in_game_year, created_at);

CREATE TABLE winter_phases (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    event_id uuid NOT NULL REFERENCES events(id) ON DELETE RESTRICT,
    in_game_year smallint NOT NULL CHECK (in_game_year BETWEEN 1 AND 9999),
    status text NOT NULL DEFAULT 'recorded' CHECK (btrim(status) <> ''),
    notes text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (campaign_id, in_game_year)
);

CREATE TABLE winter_phase_participants (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    winter_phase_id uuid NOT NULL REFERENCES winter_phases(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    history_entry_id uuid REFERENCES character_history_entries(id) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (winter_phase_id, character_id)
);

CREATE TABLE character_wound_ledger (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    source_key text NOT NULL,
    effective_year smallint NOT NULL CHECK (effective_year BETWEEN 1 AND 9999),
    sequence smallint NOT NULL DEFAULT 0 CHECK (sequence >= 0),
    damage integer NOT NULL CHECK (damage >= 0),
    treated boolean NOT NULL DEFAULT false,
    wound_source text,
    description text,
    reason text,
    recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);
CREATE INDEX character_wound_timeline_idx ON character_wound_ledger(character_id, source_key, effective_year, sequence, recorded_at);

COMMIT;
