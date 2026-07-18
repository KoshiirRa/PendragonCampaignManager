BEGIN;
CREATE TABLE squires (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
 character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT, source_key text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT timezone('utc', now()), UNIQUE(campaign_id, source_key), UNIQUE(character_id)
);
CREATE TABLE squire_service_history (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
 squire_id uuid NOT NULL REFERENCES squires(id) ON DELETE RESTRICT, knight_character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
 source_key text NOT NULL, start_year smallint NOT NULL CHECK (start_year BETWEEN 1 AND 9999),
 end_year smallint CHECK (end_year BETWEEN 1 AND 9999), start_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
 end_event_id uuid REFERENCES events(id) ON DELETE SET NULL, created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
 CHECK (end_year IS NULL OR end_year >= start_year)
);
CREATE UNIQUE INDEX squire_one_current_service_idx ON squire_service_history(squire_id) WHERE end_year IS NULL;
CREATE INDEX squire_knight_service_timeline_idx ON squire_service_history(knight_character_id,start_year,end_year);
CREATE TABLE squire_state_ledger (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
 squire_id uuid NOT NULL REFERENCES squires(id) ON DELETE RESTRICT, event_id uuid REFERENCES events(id) ON DELETE SET NULL,
 effective_year smallint NOT NULL CHECK (effective_year BETWEEN 1 AND 9999), sequence integer NOT NULL DEFAULT 0,
 category text, age integer NOT NULL CHECK (age >= 0), skill integer NOT NULL CHECK (skill >= 0),
 knight_modifier integer NOT NULL DEFAULT 0, glory integer NOT NULL DEFAULT 0 CHECK (glory >= 0),
 description text, gm_description text, reason text, recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);
CREATE INDEX squire_state_timeline_idx ON squire_state_ledger(squire_id,effective_year,sequence,recorded_at);
COMMIT;
