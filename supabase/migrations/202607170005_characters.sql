BEGIN;

CREATE TYPE character_kind AS ENUM ('player_knight', 'npc');
CREATE TYPE character_status AS ENUM ('alive', 'dead', 'missing', 'unknown');
CREATE TYPE knowledge_scope AS ENUM ('gm_only', 'players', 'shared');

CREATE TABLE characters (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    kind character_kind NOT NULL,
    name text NOT NULL,
    epithet text,
    player_name text,
    gender text,
    culture text,
    religion text,
    social_class text,
    birth_year smallint CHECK (birth_year BETWEEN 1 AND 9999),
    status character_status NOT NULL DEFAULT 'alive',
    coat_of_arms text,
    public_description text,
    foundry_uuid text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    archived_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT characters_name_not_blank CHECK (btrim(name) <> ''),
    CONSTRAINT player_knight_has_player CHECK (
        kind <> 'player_knight' OR (player_name IS NOT NULL AND btrim(player_name) <> '')
    )
);

CREATE UNIQUE INDEX characters_foundry_uuid_uq
    ON characters(campaign_id, foundry_uuid) WHERE foundry_uuid IS NOT NULL;
CREATE INDEX characters_campaign_kind_idx ON characters(campaign_id, kind, name);
CREATE INDEX characters_campaign_status_idx ON characters(campaign_id, status);
CREATE TRIGGER characters_set_updated_at
BEFORE UPDATE ON characters
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE character_status_ledger (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    session_id uuid REFERENCES campaign_sessions(id) ON DELETE SET NULL,
    status character_status NOT NULL,
    effective_year smallint NOT NULL CHECK (effective_year BETWEEN 1 AND 9999),
    sequence integer NOT NULL DEFAULT 0 CHECK (sequence >= 0),
    reason text,
    recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE INDEX character_status_ledger_current_idx
    ON character_status_ledger(character_id, effective_year DESC, sequence DESC, recorded_at DESC);

CREATE OR REPLACE FUNCTION refresh_character_current_status()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE characters
    SET status = latest.status
    FROM (
        SELECT status
        FROM character_status_ledger
        WHERE character_id = NEW.character_id
        ORDER BY effective_year DESC, sequence DESC, recorded_at DESC, id DESC
        LIMIT 1
    ) AS latest
    WHERE characters.id = NEW.character_id;
    RETURN NEW;
END;
$$;

CREATE TRIGGER character_status_ledger_refresh_current
AFTER INSERT ON character_status_ledger
FOR EACH ROW EXECUTE FUNCTION refresh_character_current_status();

CREATE TABLE character_notes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    session_id uuid REFERENCES campaign_sessions(id) ON DELETE SET NULL,
    scope knowledge_scope NOT NULL DEFAULT 'gm_only',
    note_type text NOT NULL DEFAULT 'general',
    title text,
    body text NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT character_notes_body_not_blank CHECK (btrim(body) <> ''),
    CONSTRAINT character_notes_type_not_blank CHECK (btrim(note_type) <> '')
);

CREATE INDEX character_notes_character_time_idx
    ON character_notes(character_id, recorded_at);
CREATE INDEX character_notes_campaign_scope_idx
    ON character_notes(campaign_id, scope, recorded_at);

COMMIT;
