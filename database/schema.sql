CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE place_type AS ENUM (
  'RESTAURANT',
  'ACCOMMODATION',
  'MOSQUE',
  'PRAYER_ROOM'
);

CREATE TYPE trust_status AS ENUM (
  'HALAL_CERTIFIED',
  'HALAL_CERTIFIED_SERVICE',
  'MUSLIM_OWNED',
  'MUSLIM_FRIENDLY',
  'UNVERIFIED'
);

CREATE TYPE verification_source_type AS ENUM (
  'OFFICIAL_CERTIFICATION',
  'BUSINESS_OWNER',
  'FIELD_CHECK',
  'COMMUNITY_REPORT',
  'PUBLIC_WEB_SOURCE',
  'UNKNOWN'
);

CREATE TYPE candidate_review_state AS ENUM (
  'DISCOVERED',
  'GEOCODED',
  'APPROVED',
  'PROMOTED',
  'REJECTED'
);

CREATE TABLE place_candidates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  place_type place_type NOT NULL,
  address text,
  district text,
  province text,
  phone text,
  latitude double precision,
  longitude double precision,
  proposed_trust_status trust_status NOT NULL DEFAULT 'UNVERIFIED',
  source_type verification_source_type NOT NULL DEFAULT 'UNKNOWN',
  source_reference text,
  external_provider text,
  external_id text,
  certification_number text,
  certification_expires_at timestamptz,
  review_state candidate_review_state NOT NULL DEFAULT 'DISCOVERED',
  review_note text,
  review_hold_reason text,
  source_checked_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CHECK (
    (latitude IS NULL AND longitude IS NULL)
    OR (
      latitude BETWEEN -90 AND 90
      AND longitude BETWEEN -180 AND 180
    )
  )
);

CREATE INDEX idx_place_candidates_review_state
  ON place_candidates(review_state);

CREATE INDEX idx_place_candidates_province
  ON place_candidates(province);

CREATE UNIQUE INDEX idx_place_candidates_external_ref
  ON place_candidates(external_provider, external_id)
  WHERE external_provider IS NOT NULL AND external_id IS NOT NULL;

CREATE TABLE admin_audit_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  action text NOT NULL,
  entity_type text NOT NULL,
  entity_id text,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_admin_audit_log_created_at
  ON admin_audit_log(created_at DESC);

CREATE INDEX idx_admin_audit_log_entity
  ON admin_audit_log(entity_type, entity_id);

CREATE TABLE places (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug text NOT NULL UNIQUE,
  place_type place_type NOT NULL,
  name_th text NOT NULL,
  name_en text,
  location geography(Point, 4326) NOT NULL,
  address text,
  district text,
  province text,
  postal_code text,
  phone text,
  website_url text,
  social_url text,
  active boolean NOT NULL DEFAULT true,
  source_status text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_places_location ON places USING gist (location);
CREATE INDEX idx_places_type_active ON places (place_type, active);
CREATE INDEX idx_places_province ON places (province);

CREATE TABLE place_verifications (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  place_id uuid NOT NULL REFERENCES places(id) ON DELETE CASCADE,
  claim_type text NOT NULL,
  trust_status trust_status NOT NULL,
  source_type verification_source_type NOT NULL DEFAULT 'UNKNOWN',
  source_reference text,
  verified_at timestamptz,
  expires_at timestamptz,
  note text,
  verified_by text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_place_verifications_place_id
  ON place_verifications(place_id);

CREATE INDEX idx_place_verifications_status
  ON place_verifications(trust_status);

CREATE TABLE restaurant_details (
  place_id uuid PRIMARY KEY REFERENCES places(id) ON DELETE CASCADE,
  cuisine text[],
  opening_hours jsonb,
  parking boolean,
  takeaway boolean,
  delivery boolean,
  price_level smallint CHECK (price_level BETWEEN 1 AND 4)
);

CREATE TABLE accommodation_details (
  place_id uuid PRIMARY KEY REFERENCES places(id) ON DELETE CASCADE,
  halal_food_available boolean,
  prayer_space_available boolean,
  alcohol_policy text,
  bidet_available boolean,
  family_friendly boolean,
  parking boolean,
  nearest_mosque_distance_m integer CHECK (nearest_mosque_distance_m >= 0),
  check_in_time time,
  check_out_time time
);

CREATE TABLE mosque_details (
  place_id uuid PRIMARY KEY REFERENCES places(id) ON DELETE CASCADE,
  friday_prayer boolean,
  women_prayer_area boolean,
  ablution_available boolean,
  parking boolean
);

-- Example route-corridor query.
-- :route_geom is a WGS84 LineString supplied by the API.
-- :radius_m is the selected route corridor in meters.
--
-- SELECT
--   p.id,
--   p.name_th,
--   p.place_type,
--   ST_Distance(
--     p.location,
--     ST_GeogFromText(ST_AsText(:route_geom))
--   ) AS distance_from_route_m,
--   ST_LineLocatePoint(
--     :route_geom,
--     ST_ClosestPoint(:route_geom, p.location::geometry)
--   ) AS route_progress
-- FROM places p
-- WHERE p.active = true
--   AND ST_DWithin(
--     p.location,
--     ST_GeogFromText(ST_AsText(:route_geom)),
--     :radius_m
--   )
-- ORDER BY route_progress;
