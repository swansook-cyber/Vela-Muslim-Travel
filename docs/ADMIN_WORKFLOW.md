# Admin Review Workflow

The Phase 0 admin API is intentionally small and disabled by default.

## Security

Set a strong random `ADMIN_API_KEY` only in the server environment.

Admin endpoints require:

```text
X-Admin-Key: <secret>
```

If `ADMIN_API_KEY` is empty or absent, the admin API returns HTTP 503 and cannot be used.

Do not embed this key in the public web client.

## Candidate workflow

1. Collect candidate records into staging.
2. Review source evidence.
3. Resolve and check coordinates.
4. Set state to `GEOCODED`.
5. Review trust label and certification scope.
6. Set state to `APPROVED`.
7. Promote the candidate into the production `places` table.

## Endpoints

### List candidates

```http
GET /admin/candidates
GET /admin/candidates?review_state=DISCOVERED
```

### Update review

```http
PATCH /admin/candidates/{candidate_id}
```

Example:

```json
{
  "latitude": 13.7421,
  "longitude": 100.6012,
  "review_state": "GEOCODED",
  "review_note": "Coordinates checked against current business location."
}
```

An `APPROVED` candidate must already have both latitude and longitude.

### Promote

```http
POST /admin/candidates/{candidate_id}/promote
```

Example:

```json
{
  "slug": "example-halal-restaurant",
  "name_th": "ร้านตัวอย่าง"
}
```

Promotion writes the place and its evidence-backed verification record in the same database transaction.

## Important certification boundary

A halal-certified kitchen inside a hotel is represented as `HALAL_CERTIFIED_SERVICE`. It is not converted into a claim that the entire hotel is halal-certified.


## Coordinate review

Candidate geocoding is deliberately not automatic promotion.

The admin dashboard also exposes a manual-review progress summary. It counts only
`DISCOVERED` and `GEOCODED` candidates in the pilot corridor and separates
records that are ready for approval from records still blocked by coordinate or
evidence requirements.

Reviewers can filter the active queue by readiness and blocker type:

- ready to approve,
- any blocked candidate,
- coordinate pending,
- manual review hold,
- other evidence blockers.

A province can also be selected directly from the progress summary to load that
province's queue. These controls change only the review view; they never change
candidate state.

### Manual review hold

Use `review_hold_reason` when research finds an unresolved issue that must block
approval even after coordinates are available. Examples include:

- a venue currently marked temporarily closed,
- conflicting official/public phone numbers,
- conflicting administrative addresses,
- a same-name map result that may point to a different place.

Any non-empty hold reason is returned as an approval blocker and prevents
`APPROVED`. The reviewer must resolve the issue and explicitly clear the hold
field in Admin. Candidate re-imports preserve an existing hold rather than
silently clearing it.

### Source cross-check freshness

`source_checked_at` records when the reviewer last confirmed the candidate's
public/official source identity. Approval requires this timestamp in addition to
coordinates and evidence. The 23 current pilot-corridor candidates were
cross-checked on 2026-09-25 and are stamped in the seed data.

For a new or refreshed candidate, use **ยืนยันว่าตรวจ source ตอนนี้** in Admin
after comparing the listed source, identity, address/phone and any certification
scope. The timestamp is saved with the next candidate update; it is not inferred
from `updated_at` or from review-note text.

### Coordinate verification

Coordinates are not considered reviewed merely because latitude/longitude are
present. Admin requires an explicit `coordinate_checked_at` timestamp before a
candidate can move to `GEOCODED` or `APPROVED`.

When a reviewer edits latitude/longitude or selects a new geocoder suggestion,
the current coordinate confirmation is cleared. Open the coordinate on Google
Maps, visually confirm the correct venue, then press **ยืนยันพิกัดนี้แล้ว**.
Only after that confirmation should the candidate be saved as `GEOCODED`.

### Exact Google place review links

When a candidate came from `google_business` or `google_places` and has a
stored Google place ID, the Admin review link opens that exact place via
`query_place_id`. It does not fall back to a free-text name/address search.
This is especially important for the remaining coordinate-review candidates,
where similar names or nearby businesses can otherwise produce a wrong pin.

Candidates without a Google place ID continue to use the name/address search
fallback and still require manual map verification before
`coordinate_checked_at` is recorded.

### Single-candidate review mode

Admin supports **ตรวจทีละรายการ** for mobile review. The mode displays one
candidate at a time with Previous/Next navigation while preserving the current
province, type and blocker filters. Saving a DISCOVERED candidate as GEOCODED
reloads the queue, so the reviewer can continue through the remaining filtered
work without scrolling a long card list.


The guarded review queue supports both `DISCOVERED` and `GEOCODED` candidates. This keeps source evidence, Google Maps review links, and approval blockers visible after coordinates are saved and before approval.

The admin UI:

1. searches using candidate name/address,
2. displays multiple coordinate suggestions,
3. requires an explicit coordinate choice,
4. provides a Google Maps review link,
5. saves the record as `GEOCODED` or `APPROVED` only after review.

Re-importing the discovery CSV must not erase coordinates or review state that were already checked by an admin.

## Certification freshness

A certified label is current only while its evidence has a future expiry date.

- certified candidates require a certificate number,
- certified candidates require an expiry date,
- expired certified candidates cannot be promoted,
- user-facing results flag expired verification evidence,
- the admin dashboard surfaces expired and soon-to-expire verification records.

## Operational dashboard

`/admin/dashboard` summarizes:

- total candidates,
- DISCOVERED / GEOCODED / APPROVED / PROMOTED / REJECTED counts,
- production place count,
- expired verification evidence,
- certification evidence expiring in the next 30 days.
