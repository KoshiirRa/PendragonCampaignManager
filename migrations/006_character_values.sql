BEGIN;

CREATE TABLE trait_definitions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    name text NOT NULL,
    opposed_name text NOT NULL,
    description text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (campaign_id, name),
    CONSTRAINT trait_definitions_names_not_blank CHECK (btrim(name) <> '' AND btrim(opposed_name) <> ''),
    CONSTRAINT trait_definitions_distinct_names CHECK (lower(name) <> lower(opposed_name))
);

CREATE TABLE character_trait_ledger (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    trait_definition_id uuid NOT NULL REFERENCES trait_definitions(id) ON DELETE RESTRICT,
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    session_id uuid REFERENCES campaign_sessions(id) ON DELETE SET NULL,
    effective_year smallint NOT NULL CHECK (effective_year BETWEEN 1 AND 9999),
    sequence integer NOT NULL DEFAULT 0 CHECK (sequence >= 0),
    trait_value smallint NOT NULL CHECK (trait_value >= 0),
    opposed_value smallint NOT NULL CHECK (opposed_value >= 0),
    reason text,
    recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE INDEX character_trait_ledger_current_idx
    ON character_trait_ledger(character_id, trait_definition_id, effective_year DESC, sequence DESC, recorded_at DESC);

CREATE TABLE skill_definitions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    name text NOT NULL,
    category text NOT NULL DEFAULT 'ordinary',
    description text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (campaign_id, name),
    CONSTRAINT skill_definitions_name_not_blank CHECK (btrim(name) <> ''),
    CONSTRAINT skill_definitions_category_not_blank CHECK (btrim(category) <> '')
);

CREATE TABLE character_skill_ledger (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    skill_definition_id uuid NOT NULL REFERENCES skill_definitions(id) ON DELETE RESTRICT,
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    session_id uuid REFERENCES campaign_sessions(id) ON DELETE SET NULL,
    effective_year smallint NOT NULL CHECK (effective_year BETWEEN 1 AND 9999),
    sequence integer NOT NULL DEFAULT 0 CHECK (sequence >= 0),
    value smallint NOT NULL CHECK (value >= 0),
    reason text,
    recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE INDEX character_skill_ledger_current_idx
    ON character_skill_ledger(character_id, skill_definition_id, effective_year DESC, sequence DESC, recorded_at DESC);

CREATE TABLE character_passions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    name text NOT NULL,
    subject_text text,
    related_character_id uuid REFERENCES characters(id) ON DELETE RESTRICT,
    scope knowledge_scope NOT NULL DEFAULT 'players',
    started_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    ended_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    started_year smallint CHECK (started_year BETWEEN 1 AND 9999),
    ended_year smallint CHECK (ended_year BETWEEN 1 AND 9999),
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT character_passions_name_not_blank CHECK (btrim(name) <> ''),
    CONSTRAINT character_passions_year_order CHECK (ended_year IS NULL OR started_year IS NULL OR ended_year >= started_year)
);

CREATE INDEX character_passions_character_idx ON character_passions(character_id, ended_year);

CREATE TABLE character_passion_ledger (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    passion_id uuid NOT NULL REFERENCES character_passions(id) ON DELETE RESTRICT,
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    session_id uuid REFERENCES campaign_sessions(id) ON DELETE SET NULL,
    effective_year smallint NOT NULL CHECK (effective_year BETWEEN 1 AND 9999),
    sequence integer NOT NULL DEFAULT 0 CHECK (sequence >= 0),
    value smallint NOT NULL CHECK (value >= 0),
    reason text,
    recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE INDEX character_passion_ledger_current_idx
    ON character_passion_ledger(passion_id, effective_year DESC, sequence DESC, recorded_at DESC);

COMMIT;

