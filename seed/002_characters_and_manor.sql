BEGIN;

INSERT INTO locations (id, campaign_id, parent_location_id, kind, name, description, scope)
SELECT '10000000-0000-0000-0000-000000000001', id, NULL, 'kingdom', 'Logres',
       'The sample campaign kingdom.', 'players'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO locations (id, campaign_id, parent_location_id, kind, name, description, scope)
SELECT '10000000-0000-0000-0000-000000000002', id,
       '10000000-0000-0000-0000-000000000001', 'county', 'Salisbury',
       'The sample campaign county.', 'players'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO locations (id, campaign_id, parent_location_id, kind, name, description, scope)
SELECT '10000000-0000-0000-0000-000000000003', id,
       '10000000-0000-0000-0000-000000000002', 'manor', 'Sample Manor',
       'A development manor for API and export examples.', 'players'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO characters (
    id, campaign_id, kind, name, epithet, culture, religion, social_class, status,
    public_description
)
SELECT '20000000-0000-0000-0000-000000000001', id, 'npc', 'Uther', 'Pendragon',
       'Briton', 'British Christian', 'king', 'alive', 'Sample king for development data.'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO characters (
    id, campaign_id, kind, name, culture, religion, social_class, status,
    public_description
)
SELECT '20000000-0000-0000-0000-000000000002', id, 'npc', 'Roderick',
       'Briton', 'British Christian', 'count', 'alive', 'Sample lord of Salisbury.'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO characters (
    id, campaign_id, kind, name, player_name, culture, religion, social_class,
    birth_year, status, public_description
)
SELECT '20000000-0000-0000-0000-000000000003', id, 'player_knight',
       'Sample Player Knight', 'Sample Player', 'Briton', 'British Christian',
       'vassal knight', 465, 'alive', 'A sample player knight for development.'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO character_status_ledger (
    id, campaign_id, character_id, status, effective_year, reason
)
SELECT '21000000-0000-0000-0000-000000000001', id,
       '20000000-0000-0000-0000-000000000001', 'alive', 485, 'Initial seed status.'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO character_status_ledger (
    id, campaign_id, character_id, status, effective_year, reason
)
SELECT '21000000-0000-0000-0000-000000000002', id,
       '20000000-0000-0000-0000-000000000002', 'alive', 485, 'Initial seed status.'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO character_status_ledger (
    id, campaign_id, character_id, status, effective_year, reason
)
SELECT '21000000-0000-0000-0000-000000000003', id,
       '20000000-0000-0000-0000-000000000003', 'alive', 485, 'Initial seed status.'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO manors (id, campaign_id, location_id, customary_income, notes)
SELECT '30000000-0000-0000-0000-000000000001', id,
       '10000000-0000-0000-0000-000000000003', 10.00, 'Sample manor record.'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO manor_tenures (
    id, campaign_id, manor_id, holder_character_id, liege_character_id,
    start_year, tenure_type, terms
)
SELECT '30000000-0000-0000-0000-000000000002', id,
       '30000000-0000-0000-0000-000000000001',
       '20000000-0000-0000-0000-000000000003',
       '20000000-0000-0000-0000-000000000002',
       485, 'vassalage', 'Held in return for customary knight service.'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

COMMIT;
