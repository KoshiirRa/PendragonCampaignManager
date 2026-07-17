BEGIN;

INSERT INTO campaigns (name, slug, description, current_year, timezone)
VALUES (
    'The Great Pendragon Campaign',
    'great-pendragon-campaign',
    'A sample campaign beginning during the reign of Uther Pendragon.',
    485,
    'Europe/London'
)
ON CONFLICT (slug) DO NOTHING;

COMMIT;

