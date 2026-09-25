ALTER TABLE place_candidates
ADD COLUMN IF NOT EXISTS coordinate_checked_at timestamptz;
