# Samut Songkhram / Amphawa Expansion Batch 1

Checkpoint: 2026-09-26

Samut Songkhram / Amphawa follows Samut Sakhon / Mahachai and continues the
Gulf-side central tourism corridor.

## Batch 1

`database/seeds/samut_songkhram_amphawa_expansion_review_queue.csv` contains
**8 candidates**:

- 1 mosque currently surfaced for Samut Songkhram by CICOT,
- 5 active Muslim/Halal restaurant candidates,
- 2 Amphawa accommodation candidates with explicit halal-service evidence.

All candidates begin as `DISCOVERED` with blank coordinates.

## Mosque evidence

CICOT currently surfaces Damrong Islam Mosque at Plai Phongphang, Amphawa.
Do not create extra mosque records from weak map-only evidence.

## Restaurant evidence

Current Wongnai coverage supports active Muslim/Halal discovery in Mae Klong,
including Hok Huad Islamic Food, Salma Halal, Adel, Krua Ban Nong Dana and the
halal chicken-biryani shop at PTT Khlong Khon.

Where only the provincial directory is available, exact street addresses remain
under explicit review hold rather than being guessed.

## Accommodation evidence

- The Buffalo Amphawa: current Agoda data explicitly lists halal breakfast.
- Amphawa horse farm: current Agoda data describes an on-site halal restaurant.

These are `MUSLIM_FRIENDLY` service signals and do not establish Muslim
ownership or whole-property halal certification.

## Coordinate policy

Coordinates remain blank until controlled map review or an approved resolver
provides verifiable location evidence.

## Next expansion

After this batch passes import/review quality checks, continue with
**Samut Prakan**.
