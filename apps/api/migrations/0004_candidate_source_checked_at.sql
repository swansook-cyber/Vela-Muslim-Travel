ALTER TABLE place_candidates
ADD COLUMN IF NOT EXISTS source_checked_at timestamptz;
