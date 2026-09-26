# Trat / Koh Chang Expansion Batch 1

Checkpoint: 2026-09-26

Trat / Koh Chang extends the eastern tourism coverage after Rayong / Koh Samet.

## Batch 1

`database/seeds/trat_koh_chang_expansion_review_queue.csv` contains **11
candidates**:

- 5 mosques from CICOT,
- 3 restaurant candidates,
- 3 accommodation candidates.

All begin as `DISCOVERED` with blank coordinates.

## Trust policy

Current sources show Muslim/Halal categorization, halal dining or halal breakfast
options for the commercial candidates, but do not establish Muslim ownership or
a current official certificate number.

Therefore these candidates remain `MUSLIM_FRIENDLY`.

Do not infer `MUSLIM_OWNED` from a halal menu or Islamic-sounding business
name alone, and do not promote to `HALAL_CERTIFIED` without official
certificate evidence.

## Coordinate policy

Plus Codes from public sources may be retained in the address field as source
evidence, but latitude/longitude stay blank until controlled visual map review.

## Next expansion

After this eastern tourism batch passes CI/review quality, continue with another
high-value destination such as **Mae Hong Son / Pai** or **Udon Thani**.
