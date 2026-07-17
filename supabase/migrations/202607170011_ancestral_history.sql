BEGIN;

CREATE TABLE source_references (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    source_type text NOT NULL DEFAULT 'book',
    title text NOT NULL,
    edition text,
    publication_year smallint CHECK (publication_year IS NULL OR publication_year > 0),
    notes text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (campaign_id, title, edition),
    CONSTRAINT source_references_type_not_blank CHECK (btrim(source_type) <> ''),
    CONSTRAINT source_references_title_not_blank CHECK (btrim(title) <> '')
);

CREATE TABLE family_history_entries (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    family_id uuid NOT NULL REFERENCES families(id) ON DELETE RESTRICT,
    ancestor_character_id uuid REFERENCES characters(id) ON DELETE RESTRICT,
    event_id uuid NOT NULL UNIQUE REFERENCES events(id) ON DELETE RESTRICT,
    realm_location_id uuid REFERENCES locations(id) ON DELETE RESTRICT,
    source_reference_id uuid REFERENCES source_references(id) ON DELETE RESTRICT,
    dice_log_id uuid REFERENCES dice_logs(id) ON DELETE SET NULL,
    glory_ledger_id uuid UNIQUE REFERENCES glory_ledger(id) ON DELETE SET NULL,
    start_year smallint NOT NULL CHECK (start_year BETWEEN 1 AND 9999),
    end_year smallint CHECK (end_year BETWEEN 1 AND 9999),
    entry_type text NOT NULL DEFAULT 'annual_service',
    title text NOT NULL,
    summary text NOT NULL,
    generation_method text NOT NULL DEFAULT 'manual',
    source_locator text,
    roll_expression text,
    roll_result text,
    scope knowledge_scope NOT NULL DEFAULT 'players',
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT family_history_year_order CHECK (end_year IS NULL OR end_year >= start_year),
    CONSTRAINT family_history_type_not_blank CHECK (btrim(entry_type) <> ''),
    CONSTRAINT family_history_title_not_blank CHECK (btrim(title) <> ''),
    CONSTRAINT family_history_summary_not_blank CHECK (btrim(summary) <> ''),
    CONSTRAINT family_history_method_not_blank CHECK (btrim(generation_method) <> '')
);

CREATE INDEX family_history_family_timeline_idx
    ON family_history_entries(family_id, start_year, end_year, created_at);
CREATE INDEX family_history_ancestor_timeline_idx
    ON family_history_entries(ancestor_character_id, start_year)
    WHERE ancestor_character_id IS NOT NULL;
CREATE INDEX family_history_pre_480_idx
    ON family_history_entries(campaign_id, start_year, family_id)
    WHERE start_year < 480;

COMMIT;
