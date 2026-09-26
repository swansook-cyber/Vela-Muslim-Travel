# Udon Thani Expansion Batch 1

Checkpoint: 2026-09-26

Udon Thani follows Mae Hong Son / Pai in the provincial tourism expansion.

## Batch 1

`database/seeds/udon_thani_expansion_review_queue.csv` contains **8
candidates**:

- 2 mosques currently returned for Udon Thani by CICOT,
- 3 active Muslim/Halal restaurant candidates,
- 3 accommodation candidates with explicit halal dining or breakfast evidence.

All begin as `DISCOVERED` with blank coordinates.

## Trust policy

Restaurant category labels and halal dining claims do not by themselves prove
Muslim ownership or current official certification. All commercial candidates
remain `MUSLIM_FRIENDLY` until stronger evidence is attached.

Amman Unique Hotel is especially relevant because current Agoda data explicitly
lists a halal restaurant. The Old Inn lists halal meals, and Kangaroo Residence
lists halal breakfast.

## Coordinate policy

No coordinates are inferred from text addresses. Use controlled map review or
an approved resolver before moving a candidate to `GEOCODED`.

## Next expansion

After Udon Thani passes CI/review quality, continue with **Khon Kaen**.
