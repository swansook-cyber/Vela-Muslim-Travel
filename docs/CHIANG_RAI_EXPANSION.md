# Chiang Rai Expansion Batch 1

Checkpoint: 2026-09-26

Chiang Rai is the next major northern tourism expansion after Chiang Mai.

## Coverage strategy

Prioritize:

- Chiang Rai city,
- Mae Sai,
- Mae Salong / Mae Fa Luang.

## Batch 1

`database/seeds/chiang_rai_expansion_review_queue.csv` contains **11 candidates**:

- 5 mosques from CICOT,
- 3 restaurants explicitly described as Muslim-owned,
- 3 accommodations with current halal dining/breakfast evidence.

All begin as `DISCOVERED` with blank coordinates.

## Trust policy

Salema, Khao Soi Islam Chiang Rai and Salima II are stored as
`MUSLIM_OWNED` because their reviewed sources explicitly identify Muslim
ownership.

Third-party halal-certified claims are not promoted to `HALAL_CERTIFIED`
without a current official certificate number and scope.

NAI YA Hotel and Maryo Resort are stored as `MUSLIM_FRIENDLY` because current
property data show halal dietary/breakfast options. This is not a whole-property
halal certification claim.

The Riverie by Katathani carries a review hold because current sources conflict:
Booking lists halal breakfast while Halalbooking says there is no halal food
provision. Do not approve it until the property is checked directly.

## Coordinate policy

Do not approximate coordinates from addresses. Coordinates require controlled
map review using direct map evidence, reliable current map/Plus Code,
controlled geocoding, or optional Google Place-ID resolution.

## Next expansion

Continue with **Rayong / Koh Samet** or **Trat / Koh Chang** after Chiang Rai
passes import/review quality checks.
