BEGIN;

INSERT INTO characters (id, campaign_id, kind, name, player_name, culture, religion, social_class, birth_year, status, public_description)
SELECT value.id::uuid, c.id, value.kind::character_kind, value.name, value.player_name, 'Briton',
       'British Christian', value.social_class, value.birth_year, 'alive', value.description
FROM campaigns c
CROSS JOIN (VALUES
    ('20000000-0000-0000-0000-000000000004', 'player_knight', 'Sir Cadry', 'Demo Player', 'vassal knight', 464, 'A household knight of Salisbury.'),
    ('20000000-0000-0000-0000-000000000005', 'npc', 'Sir Elad', NULL, 'household knight', 452, 'Marshal of Earl Roderick''s household.'),
    ('20000000-0000-0000-0000-000000000006', 'npc', 'Lady Elaine', NULL, 'lady', 468, 'A member of the old Vagon lineage.'),
    ('20000000-0000-0000-0000-000000000007', 'npc', 'Oswin', NULL, 'squire', 470, 'A young squire beginning his service.'),
    ('20000000-0000-0000-0000-000000000008', 'npc', 'Robert of Salisbury', NULL, 'noble heir', 470, 'Heir to the comital house of Salisbury.')
) AS value(id, kind, name, player_name, social_class, birth_year, description)
WHERE c.slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO locations (id, campaign_id, parent_location_id, kind, name, description, scope)
SELECT value.id::uuid, c.id, '10000000-0000-0000-0000-000000000002', 'manor',
       value.name, value.description, 'players'
FROM campaigns c
CROSS JOIN (VALUES
    ('10000000-0000-0000-0000-000000000004', 'Winterbourne Earls', 'A compact estate of arable fields and sheep pasture east of Sarum.'),
    ('10000000-0000-0000-0000-000000000005', 'Vagon Manor', 'A western holding near the Wylye with a mill and orchard.'),
    ('10000000-0000-0000-0000-000000000006', 'Pewsey Manor', 'A Vale of Pewsey estate recovering from poor harvests.')
) AS value(id, name, description)
WHERE c.slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO families (id, campaign_id, name, founding_year, origin_location_id, culture, religion, motto, scope, notes)
SELECT value.id::uuid, c.id, value.name, value.founding_year,
       value.location_id::uuid, 'Briton', 'British Christian', value.motto, 'players', value.notes
FROM campaigns c
CROSS JOIN (VALUES
    ('50000000-0000-0000-0000-000000000002', 'House of Vagon', 430, '10000000-0000-0000-0000-000000000005', 'The wheel endures', 'An old local lineage connected to the western manors of Salisbury.'),
    ('50000000-0000-0000-0000-000000000003', 'House of Salisbury', 420, '10000000-0000-0000-0000-000000000002', 'Steadfast in service', 'The ruling household of Salisbury and liege family to its knights.')
) AS value(id, name, founding_year, location_id, motto, notes)
WHERE c.slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO family_memberships (id, campaign_id, family_id, character_id, membership_type, start_year, is_primary, scope)
SELECT value.id::uuid, c.id, value.family_id::uuid, value.character_id::uuid,
       value.membership_type, value.start_year, true, 'players'
FROM campaigns c
CROSS JOIN (VALUES
    ('51000000-0000-0000-0000-000000000002', '50000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000004', 'birth', 464),
    ('51000000-0000-0000-0000-000000000003', '50000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000007', 'service', 485),
    ('51000000-0000-0000-0000-000000000004', '50000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000006', 'birth', 468),
    ('51000000-0000-0000-0000-000000000005', '50000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000002', 'birth', 445),
    ('51000000-0000-0000-0000-000000000006', '50000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000005', 'service', 470),
    ('51000000-0000-0000-0000-000000000007', '50000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000008', 'birth', 470)
) AS value(id, family_id, character_id, membership_type, start_year)
WHERE c.slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO manors (id, campaign_id, location_id, customary_income, population, base_defensive_value, acreage, notes)
SELECT value.id::uuid, c.id, value.location_id::uuid, value.income, value.population,
       value.defense, value.acreage, value.notes
FROM campaigns c
CROSS JOIN (VALUES
    ('30000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000004', 6.00, 180, 2, 1600, 'Held by Sir Cadry in knight service.'),
    ('30000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000005', 7.00, 230, 2, 1850, 'An inherited western manor.'),
    ('30000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000006', 5.00, 145, 1, 1400, 'A service holding in the Vale of Pewsey.')
) AS value(id, location_id, income, population, defense, acreage, notes)
WHERE c.slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO manor_tenures (id, campaign_id, manor_id, holder_character_id, liege_character_id, start_year, tenure_type, terms)
SELECT value.id::uuid, c.id, value.manor_id::uuid, value.holder_id::uuid,
       '20000000-0000-0000-0000-000000000002', 485, value.tenure_type, value.terms
FROM campaigns c
CROSS JOIN (VALUES
    ('31000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000004', 'vassalage', 'One knight of customary service.'),
    ('31000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000006', 'inheritance', 'Held by hereditary right.'),
    ('31000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000005', 'service', 'Held while serving the Salisbury household.')
) AS value(id, manor_id, holder_id, tenure_type, terms)
WHERE c.slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO events (id, campaign_id, event_type, title, description, in_game_year, in_game_date, sequence, visibility)
SELECT value.id::uuid, c.id, value.event_type, value.title, value.description,
       value.year, value.game_date, value.sequence, 'players'
FROM campaigns c
CROSS JOIN (VALUES
    ('40000000-0000-0000-0000-000000000003', 'family', 'A match proposed between two Salisbury houses', 'Lady Elaine welcomed a delegation at Winterbourne; negotiations will continue after harvest.', 485, 'High Summer', 30),
    ('40000000-0000-0000-0000-000000000004', 'winter', 'The household returns to its estates', 'Repairs were made, rents collected, and Oswin began his service as a squire.', 485, 'Winter Phase', 40),
    ('40000000-0000-0000-0000-000000000005', 'glory', 'The recovered banner is presented at court', 'Earl Roderick commended the company and ordered the banner hung in Sarum''s hall.', 486, 'February', 10),
    ('40000000-0000-0000-0000-000000000006', 'court', 'Spring court gathers at Sarum', 'The county household assembled to hear petitions and prepare for the campaigning season.', 486, 'Early Spring', 20)
) AS value(id, event_type, title, description, year, game_date, sequence)
WHERE c.slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO manor_improvements (id, campaign_id, manor_id, name, improvement_type, description)
SELECT value.id::uuid, c.id, value.manor_id::uuid, value.name, value.kind, value.description
FROM campaigns c
CROSS JOIN (VALUES
    ('60000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000003', 'Sheep fold', 'agricultural', 'Shelter supporting the manor''s wool income.'),
    ('60000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000004', 'Water mill', 'economic', 'A mill serving nearby tenants.'),
    ('60000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000004', 'Apple orchard', 'agricultural', 'A young orchard beginning to mature.'),
    ('60000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000005', 'Drainage channels', 'agricultural', 'New channels intended to recover wet fields.')
) AS value(id, manor_id, name, kind, description)
WHERE c.slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO manor_improvement_ledger (id, campaign_id, improvement_id, effective_year, status, income_modifier, maintenance_cost, recorded_at)
SELECT value.id::uuid, c.id, value.improvement_id::uuid, value.year, value.status,
       value.income, value.cost, timezone('utc', now())
FROM campaigns c
CROSS JOIN (VALUES
    ('61000000-0000-0000-0000-000000000002', '60000000-0000-0000-0000-000000000002', 483, 'sound', 0.50, 0.10),
    ('61000000-0000-0000-0000-000000000003', '60000000-0000-0000-0000-000000000003', 478, 'complete', 1.00, 0.25),
    ('61000000-0000-0000-0000-000000000004', '60000000-0000-0000-0000-000000000004', 481, 'maturing', 0.25, 0.10),
    ('61000000-0000-0000-0000-000000000005', '60000000-0000-0000-0000-000000000005', 485, 'in progress', 0.00, 0.50)
) AS value(id, improvement_id, year, status, income, cost)
WHERE c.slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO manor_assets (id, campaign_id, manor_id, asset_type, name, description)
SELECT value.id::uuid, c.id, value.manor_id::uuid, 'special_feature', value.name, value.description
FROM campaigns c
CROSS JOIN (VALUES
    ('62000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000003', 'Old boundary stone', 'Traditional meeting place for the manor court.'),
    ('62000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000004', 'Roman road frontage', 'Fast access to western markets and Sarum.'),
    ('62000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000004', 'Wylye fishing rights', 'Household food and modest rents.'),
    ('62000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000005', 'Seasonal fair', 'Three days of local trade after harvest.')
) AS value(id, manor_id, name, description)
WHERE c.slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO manor_defense_layers (id, campaign_id, manor_id, name, ring_order, defensive_value)
SELECT value.id::uuid, c.id, value.manor_id::uuid, value.name, 1, value.defense
FROM campaigns c
CROSS JOIN (VALUES
    ('63000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000003', 'Ditch and palisade', 2),
    ('63000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000004', 'Fortified stone undercroft', 3),
    ('63000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000005', 'Earth bank', 1)
) AS value(id, manor_id, name, defense)
WHERE c.slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

COMMIT;
