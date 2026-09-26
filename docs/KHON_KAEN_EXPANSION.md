# Khon Kaen Expansion Batch 1

Checkpoint: 2026-09-26

Khon Kaen follows Udon Thani in the northeastern tourism expansion.

## Batch 1

`database/seeds/khon_kaen_expansion_review_queue.csv` contains **11
candidates**:

- 5 mosques from the current CICOT directory,
- 3 active Muslim/Halal restaurant candidates,
- 3 accommodation candidates with explicit halal dining or breakfast evidence.

All candidates begin as `DISCOVERED` with blank coordinates.

## Mosque coverage

The batch uses the provincial central mosque plus four district mosques from
Mueang Khon Kaen, Ban Phai, Nong Ruea and Chum Phae. CICOT currently lists
additional Khon Kaen mosques, so Batch 1 is intentionally a useful tourism
subset rather than an assertion that these are the only mosques in the
province.

## Trust policy

Commercial candidates remain `MUSLIM_FRIENDLY`.

A Muslim/Halal category, halal menu, owner message, or hotel halal-meal option
does not by itself prove Muslim ownership or current official certification.
Do not promote to `MUSLIM_OWNED` or `HALAL_CERTIFIED` without source evidence
that explicitly supports that claim.

## Accommodation evidence

- Tonwa Resort Hotel: Booking currently lists halal dietary options for its
  restaurant.
- Avani Khon Kaen Hotel & Convention Centre: current 2026 Trip.com property
  data lists halal meals provided.
- The Garden Resort: current Agoda property data lists halal breakfast and a
  halal restaurant.

These are service-level Muslim-friendly signals, not whole-property halal
certification.

## Coordinate policy

No latitude/longitude is inferred from text addresses or map thumbnails.
Coordinates stay blank until controlled map review or an approved resolver
produces verifiable location evidence.

## Next expansion

After Khon Kaen passes import/review quality checks, continue with
**Nakhon Ratchasima / Khao Yai**.
