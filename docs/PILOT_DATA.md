# Pilot Data Workflow

## Data tiers

Vela Muslim Travel keeps trust-sensitive travel data in three separate tiers:

1. **Synthetic fixtures** — engineering tests only; never public listings.
2. **Discovery candidates** — real places from public or official sources that still require review.
3. **Production places** — reviewed coordinates and evidence that an admin explicitly approved and promoted.

The active review queue is:

`database/seeds/pilot_candidates_review_queue.csv`

Discovery data must never be promoted merely because it appears in that file.

## Current corridor

The pilot follows a real northbound Thailand drive:

นครศรีธรรมราช → สุราษฎร์ธานี → ชุมพร → ประจวบคีรีขันธ์ → เพชรบุรี → สระบุรี → นครราชสีมา / เขาใหญ่

The queue intentionally includes restaurants, mosques and accommodation rather than random nationwide pins.

## Promotion checklist

Before a candidate becomes a production listing:

- confirm the place still exists,
- resolve and manually review exact coordinates,
- confirm place type and current address/phone where practical,
- inspect the evidence behind Muslim/halal claims,
- use `HALAL_CERTIFIED` only for a restaurant with current traceable official certification,
- use `HALAL_CERTIFIED_SERVICE` for accommodation only when the evidence is service-scoped,
- otherwise use the most accurate non-certified status,
- retain source reference and review notes,
- retain certification expiry where applicable,
- reject ambiguous duplicates,
- use a unique production slug.

Promotion is blocked for same-type places within 150 m until identity is reviewed.

## Accommodation rule

Do not label an entire property halal-certified merely because:

- halal food is available,
- the property name contains "Halal",
- Muslim guests recommend it,
- it is close to a mosque,
- it has a bidet or prayer space.

Those are separate facts. Whole-property and service-level claims must remain distinct.

## Coordinate workflow

Coordinate resolution is controlled rather than automatic:

1. Admin opens a candidate.
2. The app performs an explicit geocode search.
3. Admin chooses one of the returned coordinates.
4. Admin opens the coordinate in a map for visual verification.
5. Record moves to `GEOCODED`.
6. Evidence is reviewed.
7. Record moves to `APPROVED`.
8. Admin promotes it into production.

Re-importing the discovery CSV preserves already reviewed coordinates and review state.

## Route acceptance

After the first useful production set is promoted, run:

`python -m app.tools.route_smoke`

for the real southern-Thailand → Khao Yai route at 2 km, 5 km and 10 km corridor widths.

The pilot should be judged by useful route coverage and real detour time, not by raw place count.
