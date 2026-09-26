# Rayong / Koh Samet Expansion Batch 1

Checkpoint: 2026-09-26

Rayong / Koh Samet extends tourism coverage to the eastern seaboard after
Chonburi / Pattaya.

## Batch 1

`database/seeds/rayong_koh_samet_expansion_review_queue.csv` contains **11
candidates**:

- 5 mosques from CICOT,
- 3 restaurant candidates,
- 3 Koh Samet accommodation candidates.

All begin as `DISCOVERED` with blank coordinates.

## Trust policy

The restaurant and accommodation sources show Muslim/Halal categorization,
halal dining or halal restaurant availability, but do not establish Muslim
ownership or a current official certificate number.

Therefore these entries remain `MUSLIM_FRIENDLY`.

Do not infer `MUSLIM_OWNED` from Islamic naming or a halal menu alone.

## Coordinate policy

No coordinate is inferred from a text address. Plus Codes included by sources
may be retained as address evidence, but latitude/longitude still require
controlled map review before `GEOCODED`.

## Next expansion

Continue with **Trat / Koh Chang**.
