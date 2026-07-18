BEGIN;

CREATE TABLE annual_chronicles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    winter_phase_id uuid NOT NULL REFERENCES winter_phases(id) ON DELETE RESTRICT,
    in_game_year smallint NOT NULL CHECK (in_game_year BETWEEN 1 AND 9999),
    revision integer NOT NULL CHECK (revision > 0),
    title text NOT NULL,
    opening text NOT NULL,
    closing text NOT NULL,
    status text NOT NULL DEFAULT 'published' CHECK (status IN ('draft', 'published')),
    generator_version text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (campaign_id, in_game_year, revision)
);

CREATE INDEX annual_chronicles_campaign_year_idx
    ON annual_chronicles(campaign_id, in_game_year, revision DESC);

CREATE TABLE annual_chronicle_sections (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    chronicle_id uuid NOT NULL REFERENCES annual_chronicles(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    position integer NOT NULL CHECK (position >= 0),
    heading text NOT NULL,
    body text NOT NULL,
    UNIQUE (chronicle_id, character_id),
    UNIQUE (chronicle_id, position)
);

CREATE INDEX annual_chronicle_sections_chronicle_idx
    ON annual_chronicle_sections(chronicle_id, position);

CREATE TABLE annual_chronicle_sources (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    chronicle_id uuid NOT NULL REFERENCES annual_chronicles(id) ON DELETE RESTRICT,
    section_id uuid REFERENCES annual_chronicle_sections(id) ON DELETE RESTRICT,
    event_id uuid NOT NULL REFERENCES events(id) ON DELETE RESTRICT,
    UNIQUE (chronicle_id, section_id, event_id)
);

CREATE INDEX annual_chronicle_sources_event_idx ON annual_chronicle_sources(event_id);

COMMIT;
