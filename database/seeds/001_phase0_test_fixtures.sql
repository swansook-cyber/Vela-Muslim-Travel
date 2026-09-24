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


INSERT INTO restaurant_details (
  place_id,
  cuisine,
  opening_hours,
  parking,
  takeaway,
  delivery,
  price_level
)
SELECT
  id,
  ARRAY['TEST Thai'],
  '{"mon":{"open":"08:00","close":"20:00"}}'::jsonb,
  true,
  true,
  false,
  2
FROM places
WHERE slug = 'test-route-restaurant-south'
ON CONFLICT (place_id) DO UPDATE SET
  cuisine = EXCLUDED.cuisine,
  opening_hours = EXCLUDED.opening_hours,
  parking = EXCLUDED.parking,
  takeaway = EXCLUDED.takeaway,
  delivery = EXCLUDED.delivery,
  price_level = EXCLUDED.price_level;

INSERT INTO accommodation_details (
  place_id,
  halal_food_available,
  prayer_space_available,
  alcohol_policy,
  bidet_available,
  family_friendly,
  parking,
  nearest_mosque_distance_m,
  check_in_time,
  check_out_time
)
SELECT
  id,
  true,
  true,
  'TEST_NO_ALCOHOL',
  true,
  true,
  true,
  900,
  '14:00'::time,
  '12:00'::time
FROM places
WHERE slug = 'test-route-accommodation-north'
ON CONFLICT (place_id) DO UPDATE SET
  halal_food_available = EXCLUDED.halal_food_available,
  prayer_space_available = EXCLUDED.prayer_space_available,
  alcohol_policy = EXCLUDED.alcohol_policy,
  bidet_available = EXCLUDED.bidet_available,
  family_friendly = EXCLUDED.family_friendly,
  parking = EXCLUDED.parking,
  nearest_mosque_distance_m = EXCLUDED.nearest_mosque_distance_m,
  check_in_time = EXCLUDED.check_in_time,
  check_out_time = EXCLUDED.check_out_time;

INSERT INTO mosque_details (
  place_id,
  friday_prayer,
  women_prayer_area,
  ablution_available,
  parking
)
SELECT
  id,
  true,
  true,
  true,
  true
FROM places
WHERE slug = 'test-route-mosque-middle'
ON CONFLICT (place_id) DO UPDATE SET
  friday_prayer = EXCLUDED.friday_prayer,
  women_prayer_area = EXCLUDED.women_prayer_area,
  ablution_available = EXCLUDED.ablution_available,
  parking = EXCLUDED.parking;
