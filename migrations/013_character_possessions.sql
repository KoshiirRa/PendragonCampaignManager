BEGIN;

CREATE TABLE character_stat_ledger (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    stat_code text NOT NULL,
    effective_year smallint NOT NULL CHECK (effective_year BETWEEN 1 AND 9999),
    sequence integer NOT NULL DEFAULT 0 CHECK (sequence >= 0),
    value smallint NOT NULL CHECK (value >= 0),
    reason text,
    recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    CONSTRAINT character_stat_code CHECK (stat_code IN ('siz', 'dex', 'str', 'con', 'app'))
);
CREATE INDEX character_stat_current_idx
    ON character_stat_ledger(character_id, stat_code, effective_year DESC, sequence DESC, recorded_at DESC);

CREATE TABLE inventory_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    source_key text NOT NULL,
    item_type text NOT NULL CHECK (item_type IN ('gear', 'weapon', 'armour')),
    name text NOT NULL CHECK (btrim(name) <> ''),
    description text,
    libra integer NOT NULL DEFAULT 0 CHECK (libra >= 0),
    denarii integer NOT NULL DEFAULT 0 CHECK (denarii >= 0),
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (campaign_id, source_key)
);

CREATE TABLE weapon_profiles (
    inventory_item_id uuid PRIMARY KEY REFERENCES inventory_items(id) ON DELETE RESTRICT,
    skill text,
    damage_formula text,
    weapon_range text,
    mounted_use text,
    melee boolean NOT NULL DEFAULT true
);

CREATE TABLE armour_profiles (
    inventory_item_id uuid PRIMARY KEY REFERENCES inventory_items(id) ON DELETE RESTRICT,
    armour_points smallint NOT NULL DEFAULT 0,
    material text,
    is_shield boolean NOT NULL DEFAULT false
);

CREATE TABLE character_inventory_ledger (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    inventory_item_id uuid NOT NULL REFERENCES inventory_items(id) ON DELETE RESTRICT,
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    effective_year smallint NOT NULL CHECK (effective_year BETWEEN 1 AND 9999),
    sequence integer NOT NULL DEFAULT 0 CHECK (sequence >= 0),
    quantity integer NOT NULL CHECK (quantity >= 0),
    equipped boolean NOT NULL DEFAULT false,
    reason text,
    recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);
CREATE INDEX character_inventory_current_idx
    ON character_inventory_ledger(character_id, inventory_item_id, effective_year DESC, sequence DESC, recorded_at DESC);

CREATE TABLE horses (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    source_key text NOT NULL,
    name text NOT NULL CHECK (btrim(name) <> ''),
    breed text,
    colour text,
    personality text,
    features text,
    description text,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE (campaign_id, source_key)
);

CREATE TABLE horse_ownership_history (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    horse_id uuid NOT NULL REFERENCES horses(id) ON DELETE RESTRICT,
    character_id uuid NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
    start_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    end_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    start_year smallint NOT NULL CHECK (start_year BETWEEN 1 AND 9999),
    end_year smallint CHECK (end_year BETWEEN 1 AND 9999),
    CONSTRAINT horse_ownership_year_order CHECK (end_year IS NULL OR end_year >= start_year)
);
CREATE UNIQUE INDEX horse_open_owner_idx ON horse_ownership_history(horse_id) WHERE end_year IS NULL;
CREATE INDEX horse_owner_history_idx ON horse_ownership_history(character_id, start_year, end_year);

CREATE TABLE horse_stat_ledger (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
    horse_id uuid NOT NULL REFERENCES horses(id) ON DELETE RESTRICT,
    event_id uuid REFERENCES events(id) ON DELETE SET NULL,
    effective_year smallint NOT NULL CHECK (effective_year BETWEEN 1 AND 9999),
    sequence integer NOT NULL DEFAULT 0 CHECK (sequence >= 0),
    siz smallint NOT NULL DEFAULT 0 CHECK (siz >= 0),
    dex smallint NOT NULL DEFAULT 0 CHECK (dex >= 0),
    str smallint NOT NULL DEFAULT 0 CHECK (str >= 0),
    con smallint NOT NULL DEFAULT 0 CHECK (con >= 0),
    hp smallint NOT NULL DEFAULT 0 CHECK (hp >= 0),
    max_hp smallint NOT NULL DEFAULT 0 CHECK (max_hp >= 0),
    move smallint NOT NULL DEFAULT 0 CHECK (move >= 0),
    armour smallint NOT NULL DEFAULT 0 CHECK (armour >= 0),
    horse_armour smallint NOT NULL DEFAULT 0 CHECK (horse_armour >= 0),
    age smallint NOT NULL DEFAULT 0 CHECK (age >= 0),
    equipped boolean NOT NULL DEFAULT false,
    reason text,
    recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);
CREATE INDEX horse_stat_current_idx
    ON horse_stat_ledger(horse_id, effective_year DESC, sequence DESC, recorded_at DESC);

COMMIT;
