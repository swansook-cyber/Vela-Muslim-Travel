# Mae Hong Son / Pai Expansion Batch 1

Checkpoint: 2026-09-26

Mae Hong Son / Pai is the next destination after Trat / Koh Chang in the
tourism expansion sequence.

## Batch 1

`database/seeds/mae_hong_son_pai_expansion_review_queue.csv` contains **9
candidates**:

- 3 mosques from the current CICOT directory,
- 4 current restaurant candidates,
- 2 Pai accommodation candidates with explicit halal-breakfast evidence.

All begin as `DISCOVERED` with blank coordinates.

## Why only three mosques

The current CICOT directory returns three Mae Hong Son mosques: Nurut Takwa in
Mueang Mae Hong Son, Isra in Pai, and Jamiatul Islam in Mae Sariang.

Do not force a five-mosque quota by inventing or weakening source standards.

## Trust policy

The commercial sources currently establish Muslim/Halal categorization or halal
breakfast availability, but they do not establish Muslim ownership or a current
official certificate number.

Therefore all restaurant and accommodation candidates remain
`MUSLIM_FRIENDLY`.

If later evidence explicitly establishes Muslim ownership, promote that field
through the normal evidence review. Do not infer ownership from a business name,
menu label, or category alone.

## Coordinate policy

No latitude/longitude is inferred from text addresses or third-party map
snippets. Coordinates remain blank until controlled map review or an approved
resolver supplies verifiable map evidence.

## Historical source note

Older Tourism Authority of Thailand halal guides contain several Mae Hong Son
restaurant names. They are useful discovery evidence only and are not treated as
proof that those venues are still operating in 2026.

## Next expansion

After this batch passes CI/review quality, continue with **Udon Thani**.
