BEGIN;

ALTER TABLE family_memberships ADD COLUMN source_key text;
ALTER TABLE character_parentage ADD COLUMN source_key text;
ALTER TABLE marriages ADD COLUMN source_key text;
ALTER TABLE inheritance_cases ADD COLUMN source_key text;
ALTER TABLE inheritance_heirs ADD COLUMN source_key text;

CREATE UNIQUE INDEX family_memberships_source_uq ON family_memberships(campaign_id, source_key) WHERE source_key IS NOT NULL;
CREATE UNIQUE INDEX character_parentage_source_uq ON character_parentage(campaign_id, source_key) WHERE source_key IS NOT NULL;
CREATE UNIQUE INDEX marriages_source_uq ON marriages(campaign_id, source_key) WHERE source_key IS NOT NULL;
CREATE UNIQUE INDEX inheritance_cases_source_uq ON inheritance_cases(campaign_id, source_key) WHERE source_key IS NOT NULL;
CREATE UNIQUE INDEX inheritance_heirs_source_uq ON inheritance_heirs(campaign_id, source_key) WHERE source_key IS NOT NULL;

COMMIT;
