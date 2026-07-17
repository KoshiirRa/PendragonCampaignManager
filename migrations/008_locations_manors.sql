BEGIN;

CREATE TYPE location_kind AS ENUM (
    'kingdom', 'county', 'barony', 'manor', 'holding', 'settlement',
    'castle', 'church', 'forest', 'road', 'other'
);

CREATE TABLE locations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    parent_location_id uuid REFERENCES locations(id) ON DELETE RESTRICT,
    kind location_kind NOT NULL,
    name text NOT NULL,
    description text,
    scope knowledge_scope NOT NULL DEFAULT 'players',
    latitude numeric(9,6),
    longitude numeric(9,6),
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    archived_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT locations_name_not_blank CHECK (btrim(name) <> ''),
    CONSTRAINT locations_not_own_parent CHECK (parent_location_id IS NULL OR parent_location_id <> id),
    CONSTRAINT locations_latitude_range CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT locations_longitude_range CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180)
);

CREATE INDEX locations_campaign_parent_idx ON locations(campaign_id, parent_location_id, kind);
CREATE INDEX locations_campaign_name_idx ON locations(campaign_id, name);
CREATE TRIGGER locations_set_updated_at
BEFORE UPDATE ON locations
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE location_connections (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    from_location_id uuid NOT NULL REFERENCES locations(id) ON DELETE RESTRICT,
    to_location_id uuid NOT NULL REFERENCES locations(id) ON DELETE RESTRICT,
    relationship_type text NOT NULL DEFAULT 'route',
    distance_miles numeric(8,2) CHECK (distance_miles IS NULL OR distance_miles >= 0),
    notes text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (from_location_id, to_location_id, relationship_type),
    CONSTRAINT location_connections_distinct CHECK (from_location_id <> to_location_id),
    CONSTRAINT location_connections_type_not_blank CHECK (btrim(relationship_type) <> '')
);

CREATE INDEX location_connections_reverse_idx ON location_connections(to_location_id, from_location_id);

CREATE TABLE manors (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    location_id uuid NOT NULL UNIQUE REFERENCES locations(id) ON DELETE RESTRICT,
    customary_income numeric(12,2) CHECK (customary_income IS NULL OR customary_income >= 0),
    acreage integer CHECK (acreage IS NULL OR acreage >= 0),
    notes text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE INDEX manors_campaign_idx ON manors(campaign_id);
CREATE TRIGGER manors_set_updated_at
BEFORE UPDATE ON manors
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE manor_tenures (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    manor_id uuid NOT NULL REFERENCES manors(id) ON DELETE RESTRICT,
    holder_character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    liege_character_id uuid REFERENCES characters(id) ON DELETE RESTRICT,
    start_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    end_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    start_year smallint NOT NULL CHECK (start_year BETWEEN 1 AND 9999),
    end_year smallint CHECK (end_year BETWEEN 1 AND 9999),
    tenure_type text NOT NULL DEFAULT 'grant',
    terms text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT manor_tenures_year_order CHECK (end_year IS NULL OR end_year >= start_year),
    CONSTRAINT manor_tenures_type_not_blank CHECK (btrim(tenure_type) <> '')
);

CREATE UNIQUE INDEX manor_tenures_one_current_holder_uq
    ON manor_tenures(manor_id) WHERE end_year IS NULL;
CREATE INDEX manor_tenures_holder_idx ON manor_tenures(holder_character_id, start_year, end_year);

CREATE TABLE manor_improvements (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    manor_id uuid NOT NULL REFERENCES manors(id) ON DELETE RESTRICT,
    name text NOT NULL,
    improvement_type text NOT NULL,
    description text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT manor_improvements_name_not_blank CHECK (btrim(name) <> ''),
    CONSTRAINT manor_improvements_type_not_blank CHECK (btrim(improvement_type) <> '')
);

CREATE INDEX manor_improvements_manor_idx ON manor_improvements(manor_id);

CREATE TABLE manor_improvement_ledger (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    improvement_id uuid NOT NULL REFERENCES manor_improvements(id) ON DELETE RESTRICT,
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    effective_year smallint NOT NULL CHECK (effective_year BETWEEN 1 AND 9999),
    status text NOT NULL,
    income_modifier numeric(12,2) NOT NULL DEFAULT 0,
    maintenance_cost numeric(12,2) NOT NULL DEFAULT 0 CHECK (maintenance_cost >= 0),
    notes text,
    recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT manor_improvement_ledger_status_not_blank CHECK (btrim(status) <> '')
);

CREATE INDEX manor_improvement_ledger_current_idx
    ON manor_improvement_ledger(improvement_id, effective_year DESC, recorded_at DESC);

COMMIT;
