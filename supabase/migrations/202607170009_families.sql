BEGIN;

CREATE TABLE families (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    name text NOT NULL,
    founding_year smallint CHECK (founding_year BETWEEN 1 AND 9999),
    dissolved_year smallint CHECK (dissolved_year BETWEEN 1 AND 9999),
    origin_location_id uuid REFERENCES locations(id) ON DELETE RESTRICT,
    culture text,
    religion text,
    coat_of_arms text,
    motto text,
    scope knowledge_scope NOT NULL DEFAULT 'players',
    notes text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    archived_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT families_name_not_blank CHECK (btrim(name) <> ''),
    CONSTRAINT families_year_order CHECK (dissolved_year IS NULL OR founding_year IS NULL OR dissolved_year >= founding_year)
);

CREATE INDEX families_campaign_name_idx ON families(campaign_id, name);
CREATE TRIGGER families_set_updated_at
BEFORE UPDATE ON families
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE family_memberships (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    family_id uuid NOT NULL REFERENCES families(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    membership_type text NOT NULL DEFAULT 'birth',
    branch_name text,
    start_year smallint CHECK (start_year BETWEEN 1 AND 9999),
    end_year smallint CHECK (end_year BETWEEN 1 AND 9999),
    start_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    end_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    is_primary boolean NOT NULL DEFAULT true,
    scope knowledge_scope NOT NULL DEFAULT 'players',
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT family_memberships_type_not_blank CHECK (btrim(membership_type) <> ''),
    CONSTRAINT family_memberships_year_order CHECK (end_year IS NULL OR start_year IS NULL OR end_year >= start_year)
);

CREATE INDEX family_memberships_family_idx ON family_memberships(family_id, start_year, end_year);
CREATE INDEX family_memberships_character_idx ON family_memberships(character_id, start_year, end_year);
CREATE UNIQUE INDEX family_memberships_current_primary_uq
    ON family_memberships(character_id) WHERE is_primary AND end_year IS NULL;

CREATE TABLE character_parentage (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    parent_character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    child_character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    relationship_type text NOT NULL DEFAULT 'biological',
    certainty text NOT NULL DEFAULT 'confirmed',
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    scope knowledge_scope NOT NULL DEFAULT 'players',
    notes text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (parent_character_id, child_character_id, relationship_type),
    CONSTRAINT character_parentage_distinct CHECK (parent_character_id <> child_character_id),
    CONSTRAINT character_parentage_type_not_blank CHECK (btrim(relationship_type) <> ''),
    CONSTRAINT character_parentage_certainty_not_blank CHECK (btrim(certainty) <> '')
);

CREATE INDEX character_parentage_child_idx ON character_parentage(child_character_id);

CREATE TABLE marriages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    spouse_one_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    spouse_two_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    start_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    end_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    start_year smallint NOT NULL CHECK (start_year BETWEEN 1 AND 9999),
    end_year smallint CHECK (end_year BETWEEN 1 AND 9999),
    end_reason text,
    scope knowledge_scope NOT NULL DEFAULT 'players',
    notes text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT marriages_distinct_spouses CHECK (spouse_one_id <> spouse_two_id),
    CONSTRAINT marriages_canonical_order CHECK (spouse_one_id < spouse_two_id),
    CONSTRAINT marriages_year_order CHECK (end_year IS NULL OR end_year >= start_year)
);

CREATE UNIQUE INDEX marriages_current_pair_uq
    ON marriages(spouse_one_id, spouse_two_id) WHERE end_year IS NULL;
CREATE INDEX marriages_spouse_two_idx ON marriages(spouse_two_id, start_year, end_year);

COMMIT;

