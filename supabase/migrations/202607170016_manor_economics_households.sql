BEGIN;
ALTER TABLE manors ADD COLUMN assized_rent numeric(12,2) CHECK (assized_rent IS NULL OR assized_rent >= 0);
ALTER TABLE manors ADD COLUMN population integer CHECK (population IS NULL OR population >= 0);
ALTER TABLE manors ADD COLUMN base_defensive_value integer NOT NULL DEFAULT 1 CHECK (base_defensive_value >= 0);

CREATE TABLE manor_annual_resolutions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
 manor_id uuid NOT NULL REFERENCES manors(id) ON DELETE RESTRICT, event_id uuid NOT NULL REFERENCES events(id) ON DELETE RESTRICT,
 winter_phase_id uuid REFERENCES winter_phases(id) ON DELETE RESTRICT, in_game_year smallint NOT NULL CHECK (in_game_year BETWEEN 1 AND 9999),
 steward_character_id uuid REFERENCES characters(id) ON DELETE RESTRICT, stewardship_value integer CHECK (stewardship_value IS NULL OR stewardship_value >= 0),
 roll_result text NOT NULL, income numeric(12,2) NOT NULL DEFAULT 0, expenses numeric(12,2) NOT NULL DEFAULT 0,
 privy_funds numeric(12,2) NOT NULL DEFAULT 0, famine_stage smallint NOT NULL DEFAULT 0 CHECK (famine_stage >= 0),
 population_change integer NOT NULL DEFAULT 0, notes text, created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
 UNIQUE(manor_id,in_game_year), CHECK (btrim(roll_result) <> '')
);
CREATE TABLE manor_treasury_ledger (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
 manor_id uuid NOT NULL REFERENCES manors(id) ON DELETE RESTRICT, event_id uuid REFERENCES events(id) ON DELETE SET NULL,
 annual_resolution_id uuid REFERENCES manor_annual_resolutions(id) ON DELETE RESTRICT, in_game_year smallint NOT NULL CHECK (in_game_year BETWEEN 1 AND 9999),
 amount numeric(12,2) NOT NULL CHECK (amount <> 0), category text NOT NULL, description text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT timezone('utc', now()), CHECK (btrim(category) <> ''), CHECK (btrim(description) <> '')
);
CREATE INDEX manor_treasury_timeline_idx ON manor_treasury_ledger(manor_id,in_game_year,created_at);
CREATE TABLE manor_assets (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
 manor_id uuid NOT NULL REFERENCES manors(id) ON DELETE RESTRICT, asset_type text NOT NULL, name text NOT NULL,
 description text, created_at timestamptz NOT NULL DEFAULT timezone('utc', now()), UNIQUE(manor_id,asset_type,name)
);
CREATE TABLE manor_asset_ledger (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
 asset_id uuid NOT NULL REFERENCES manor_assets(id) ON DELETE RESTRICT, event_id uuid REFERENCES events(id) ON DELETE SET NULL,
 effective_year smallint NOT NULL CHECK (effective_year BETWEEN 1 AND 9999), quantity numeric(12,2), status text NOT NULL,
 annual_income numeric(12,2) NOT NULL DEFAULT 0, annual_cost numeric(12,2) NOT NULL DEFAULT 0, notes text,
 recorded_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);
CREATE TABLE household_employment_history (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
 manor_id uuid NOT NULL REFERENCES manors(id) ON DELETE RESTRICT, character_id uuid REFERENCES characters(id) ON DELETE RESTRICT,
 name text NOT NULL, role text NOT NULL, social_rank text, key_skill text, key_skill_value integer CHECK (key_skill_value IS NULL OR key_skill_value >= 0),
 annual_cost numeric(12,2) NOT NULL DEFAULT 0 CHECK (annual_cost >= 0), start_year smallint NOT NULL CHECK (start_year BETWEEN 1 AND 9999),
 end_year smallint CHECK (end_year BETWEEN 1 AND 9999), start_event_id uuid REFERENCES events(id) ON DELETE SET NULL,
 end_event_id uuid REFERENCES events(id) ON DELETE SET NULL, notes text, created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
 CHECK (end_year IS NULL OR end_year >= start_year)
);
CREATE TABLE manor_defense_layers (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE RESTRICT,
 manor_id uuid NOT NULL REFERENCES manors(id) ON DELETE RESTRICT, name text NOT NULL, ring_order smallint NOT NULL CHECK (ring_order >= 0),
 defensive_value integer NOT NULL, construction_cost numeric(12,2) CHECK (construction_cost IS NULL OR construction_cost >= 0),
 improvement_id uuid REFERENCES manor_improvements(id) ON DELETE RESTRICT, UNIQUE(manor_id,ring_order,name)
);
COMMIT;
