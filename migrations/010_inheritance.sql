BEGIN;

CREATE TABLE inheritance_cases (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    decedent_character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    opened_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    settled_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    opened_year smallint NOT NULL CHECK (opened_year BETWEEN 1 AND 9999),
    settled_year smallint CHECK (settled_year BETWEEN 1 AND 9999),
    governing_custom text,
    will_summary text,
    scope knowledge_scope NOT NULL DEFAULT 'players',
    notes text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT inheritance_cases_year_order CHECK (settled_year IS NULL OR settled_year >= opened_year)
);

CREATE INDEX inheritance_cases_decedent_idx ON inheritance_cases(decedent_character_id, opened_year);

CREATE TABLE inheritance_heirs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    inheritance_case_id uuid NOT NULL REFERENCES inheritance_cases(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    priority smallint CHECK (priority IS NULL OR priority > 0),
    relationship_description text,
    claim_status text NOT NULL DEFAULT 'potential',
    designated boolean NOT NULL DEFAULT false,
    notes text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (inheritance_case_id, character_id),
    CONSTRAINT inheritance_heirs_status_not_blank CHECK (btrim(claim_status) <> '')
);

CREATE INDEX inheritance_heirs_character_idx ON inheritance_heirs(character_id);

CREATE TABLE inheritance_manor_transfers (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    inheritance_case_id uuid NOT NULL REFERENCES inheritance_cases(id) ON DELETE RESTRICT,
    manor_id uuid NOT NULL REFERENCES manors(id) ON DELETE RESTRICT,
    beneficiary_character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    event_id uuid NOT NULL REFERENCES events(id) ON DELETE RESTRICT,
    transferred_year smallint NOT NULL CHECK (transferred_year BETWEEN 1 AND 9999),
    terms text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (inheritance_case_id, manor_id)
);

CREATE INDEX inheritance_manor_transfers_beneficiary_idx
    ON inheritance_manor_transfers(beneficiary_character_id, transferred_year);

COMMIT;

