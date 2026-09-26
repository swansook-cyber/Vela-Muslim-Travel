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
7. Run promotion preflight.
8. Promote the candidate into the production `places` table.

Forward review states cannot be skipped. In particular, Admin rejects a direct
`DISCOVERED → APPROVED` update.

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
province's queue. Admin also provides shortcuts for the Google-resolvable queue,
the GEOCODED candidates that are ready to approve, and the APPROVED candidates
waiting for promotion. These controls change only the review view; they never
change candidate state.

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
stored Google place ID, the Admin review link uses Google's documented
`query=PLACE_NAME&query_place_id=PLACE_ID` form. This targets the stored place
ID while retaining the required search query parameter.

Candidates without a Google place ID continue to use the name/address search
fallback and still require manual map verification before
`coordinate_checked_at` is recorded.

### Optional Google Place coordinate resolver

If the server has `GOOGLE_PLACES_API_KEY` configured, Admin exposes
**ดึงพิกัดจาก Google Place ID** for Google-backed candidates. The API requests
only the Place Details fields `id,location`.

The resolver is deliberately read-only:

1. it returns a coordinate suggestion,
2. Admin fills latitude/longitude and clears any previous coordinate
   confirmation,
3. the reviewer opens the coordinate on Google Maps,
4. the reviewer explicitly presses **ยืนยันพิกัดนี้แล้ว**,
5. only then can the candidate be saved as `GEOCODED`.

If the key is absent, the resolver returns a configuration error and the normal
Nominatim/manual review workflow remains available. The Google key stays on the
server and must never be embedded in the public web bundle. Google Places usage
may incur charges according to the account's Maps Platform billing setup.
Successful Place ID resolutions are cached server-side (24 hours by default)
to avoid repeated provider requests and unnecessary cost when a reviewer opens
the same candidate more than once.

### Batch Google coordinate suggestions

When the Google Places resolver is configured, Admin also offers
**ดึง Google พิกัด N รายการ** for the currently filtered DISCOVERED queue.
This is a convenience action only:

1. each Google-backed candidate is resolved by its stored Place ID,
2. the returned coordinates are copied into that candidate's local Admin draft,
3. no candidate state is changed,
4. `coordinate_checked_at` remains empty,
5. each coordinate must still be opened on the map and explicitly confirmed
   before saving as `GEOCODED`.

The browser sends one batch request. The API resolves candidates sequentially
rather than flooding the provider, and the server-side Place resolver cache is
reused. The batch is capped at 25 candidate IDs. Per-candidate failures are
returned alongside successes, so one bad or missing candidate does not discard
successful draft suggestions.

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


### Promotion preflight

Before an APPROVED candidate can be promoted from Admin, run
**ตรวจ duplicate / slug**.

The preflight is read-only and checks:

- whether the proposed production slug already exists,
- whether an active production place of the same type is within 150 m.

Admin enables the final **Promote เข้า production** action only after the
preflight passes. Promotion performs the same checks again server-side before
writing, so a stale browser preflight cannot bypass duplicate protection.

A nearby match is not automatically deleted or merged. It must be reviewed as
a potential duplicate and resolved deliberately.


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
