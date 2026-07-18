BEGIN;

UPDATE campaigns
SET slug = 'salisbury'
WHERE slug = 'great-pendragon-campaign'
  AND NOT EXISTS (SELECT 1 FROM campaigns WHERE slug = 'salisbury');

COMMIT;
