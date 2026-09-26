# Prachuap Khiri Khan / Hua Hin Expansion Batch 1

Checkpoint: 2026-09-26

Prachuap Khiri Khan / Hua Hin follows Nakhon Ratchasima / Khao Yai in the
tourism expansion.

## Batch 1

`database/seeds/prachuap_hua_hin_expansion_review_queue.csv` contains **11
candidates**:

- 5 mosques from the current CICOT directory,
- 3 active Hua Hin Muslim/Halal restaurant candidates,
- 3 accommodation candidates with explicit current halal dining evidence.

All candidates begin as `DISCOVERED` with blank coordinates.

## Mosque coverage

CICOT currently lists substantially more than five mosques in Prachuap Khiri
Khan. Batch 1 intentionally samples useful coverage across Pran Buri, Mueang
Prachuap Khiri Khan, Thap Sakae and Sam Roi Yot instead of pretending to be a
complete provincial mosque inventory.

## Restaurant evidence

- Bombay Palace Indian Restaurant Huahin is currently categorized Muslim/Halal
  on Wongnai and is active at 27/1 Soi Dechanuchit.
- Mooz Hua Hin appears in Wongnai's current Prachuap Muslim/Halal directory and
  Tripadvisor's current 2026 Hua Hin halal results. Exact street address is held
  for direct review.
- Halal Seafood @ Hua Hin has a current active Wongnai listing at Golf View.

These signals justify `MUSLIM_FRIENDLY`, not automatic
`MUSLIM_OWNED` or `HALAL_CERTIFIED`.

## Accommodation evidence

- Hua Hin Marriott Resort and Spa: current Booking data lists halal dietary
  options at multiple on-site restaurants.
- Golden Sea Hua Hin: Booking lists halal dietary options at its restaurant.
- @T Boutique Hotel: current Agoda data explicitly lists a halal restaurant.

These are service-level Muslim-friendly signals and do not imply whole-property
halal certification.

## Coordinate policy

No latitude/longitude is copied from aggregator map widgets or inferred from
addresses. Coordinates stay blank until controlled map review or an approved
resolver provides verifiable evidence.

## Next expansion

After Prachuap / Hua Hin passes import/review quality checks, continue with
**Phetchaburi / Cha-am** to complete the adjoining Gulf tourism corridor.
