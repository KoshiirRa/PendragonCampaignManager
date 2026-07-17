BEGIN;

ALTER TABLE trait_definitions ADD COLUMN source_key text;
ALTER TABLE skill_definitions ADD COLUMN source_key text;
ALTER TABLE character_passions ADD COLUMN source_key text;

CREATE UNIQUE INDEX trait_definitions_source_key_idx
    ON trait_definitions(campaign_id, source_key) WHERE source_key IS NOT NULL;
CREATE UNIQUE INDEX skill_definitions_source_key_idx
    ON skill_definitions(campaign_id, source_key) WHERE source_key IS NOT NULL;
CREATE UNIQUE INDEX character_passions_source_key_idx
    ON character_passions(character_id, source_key) WHERE source_key IS NOT NULL;

ALTER TABLE trait_definitions
    ADD CONSTRAINT trait_definitions_source_key_not_blank
    CHECK (source_key IS NULL OR btrim(source_key) <> '');
ALTER TABLE skill_definitions
    ADD CONSTRAINT skill_definitions_source_key_not_blank
    CHECK (source_key IS NULL OR btrim(source_key) <> '');
ALTER TABLE character_passions
    ADD CONSTRAINT character_passions_source_key_not_blank
    CHECK (source_key IS NULL OR btrim(source_key) <> '');

COMMIT;
