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
