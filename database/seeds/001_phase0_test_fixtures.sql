-- Synthetic Phase 0 fixtures.
-- These records are NOT real businesses and must never be exposed as production listings.
-- They exist only to validate PostGIS route-corridor and ordering behavior.

INSERT INTO places (
  slug,
  place_type,
  name_th,
  name_en,
  location,
  province,
  active,
  source_status
)
VALUES
  (
    'test-route-restaurant-south',
    'RESTAURANT',
    'TEST ร้านอาหาร จุดใต้',
    'TEST Restaurant South',
    ST_SetSRID(ST_MakePoint(99.9500, 11.8000), 4326)::geography,
    'TEST',
    true,
    'TEST_FIXTURE'
  ),
  (
    'test-route-mosque-middle',
    'MOSQUE',
    'TEST มัสยิด จุดกลาง',
    'TEST Mosque Middle',
    ST_SetSRID(ST_MakePoint(100.2000, 12.6000), 4326)::geography,
    'TEST',
    true,
    'TEST_FIXTURE'
  ),
  (
    'test-route-accommodation-north',
    'ACCOMMODATION',
    'TEST ที่พัก จุดเหนือ',
    'TEST Accommodation North',
    ST_SetSRID(ST_MakePoint(100.4500, 13.3000), 4326)::geography,
    'TEST',
    true,
    'TEST_FIXTURE'
  ),
  (
    'test-route-far-away',
    'RESTAURANT',
    'TEST ร้านไกลเส้นทาง',
    'TEST Far Away Restaurant',
    ST_SetSRID(ST_MakePoint(102.5000, 12.6000), 4326)::geography,
    'TEST',
    true,
    'TEST_FIXTURE'
  )
ON CONFLICT (slug) DO NOTHING;

INSERT INTO place_verifications (
  place_id,
  claim_type,
  trust_status,
  source_type,
  source_reference,
  verified_at,
  note,
  verified_by
)
SELECT
  p.id,
  'TEST_ONLY',
  'UNVERIFIED',
  'UNKNOWN',
  'synthetic://phase0-test-fixture',
  now(),
  'Synthetic fixture. Not a real-world halal or Muslim-friendly claim.',
  'SYSTEM_TEST'
FROM places p
WHERE p.source_status = 'TEST_FIXTURE'
  AND NOT EXISTS (
    SELECT 1
    FROM place_verifications pv
    WHERE pv.place_id = p.id
      AND pv.claim_type = 'TEST_ONLY'
  );
