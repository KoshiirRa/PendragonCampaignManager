BEGIN;

-- Representative, player-visible records for the disposable development campaign.
INSERT INTO events (id, campaign_id, event_type, title, description, in_game_year, in_game_date, sequence, visibility)
SELECT '40000000-0000-0000-0000-000000000001', id, 'court',
       'The young knight takes the oath',
       'Before Earl Roderick at Sarum, the household knight swore service to Salisbury.',
       485, 'Early Spring', 10, 'players'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO events (id, campaign_id, event_type, title, description, in_game_year, in_game_date, sequence, visibility)
SELECT '40000000-0000-0000-0000-000000000002', id, 'battle',
       'Raiders driven from the Avon valley',
       'A hurried pursuit recovered the stolen herd at a rain-swollen ford.',
       485, 'May', 20, 'players'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO families (id, campaign_id, name, founding_year, origin_location_id, culture, religion, motto, scope, notes)
SELECT '50000000-0000-0000-0000-000000000001', id, 'House of Winterbourne', 440,
       '10000000-0000-0000-0000-000000000003', 'Briton', 'British Christian',
       'By oath and earth', 'players', 'A Salisbury knightly family bound to Earl Roderick.'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO family_memberships (id, campaign_id, family_id, character_id, membership_type, start_year, is_primary, scope)
SELECT '51000000-0000-0000-0000-000000000001', id,
       '50000000-0000-0000-0000-000000000001',
       '20000000-0000-0000-0000-000000000003', 'birth', 465, true, 'players'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO manor_improvements (id, campaign_id, manor_id, name, improvement_type, description)
SELECT '60000000-0000-0000-0000-000000000001', id,
       '30000000-0000-0000-0000-000000000001', 'Timber hall', 'building',
       'The household hall and center of manor administration.'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO manor_improvement_ledger (id, campaign_id, improvement_id, effective_year, status, income_modifier, maintenance_cost, notes, recorded_at)
SELECT '61000000-0000-0000-0000-000000000001', id,
       '60000000-0000-0000-0000-000000000001', 480, 'complete', 0, 0.25,
       'Standing at the opening of the campaign.', timezone('utc', now())
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO manor_assets (id, campaign_id, manor_id, asset_type, name, description)
SELECT '62000000-0000-0000-0000-000000000001', id,
       '30000000-0000-0000-0000-000000000001', 'special_feature', 'Clear spring',
       'Reliable water through the driest summers.'
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

INSERT INTO manor_defense_layers (id, campaign_id, manor_id, name, ring_order, defensive_value)
SELECT '63000000-0000-0000-0000-000000000001', id,
       '30000000-0000-0000-0000-000000000001', 'Ditch and palisade', 1, 2
FROM campaigns WHERE slug = 'salisbury'
ON CONFLICT (id) DO NOTHING;

COMMIT;
