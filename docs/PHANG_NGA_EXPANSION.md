# Phang Nga Expansion Batch 1

Checkpoint: 2026-09-26

Phang Nga intentionally uses a smaller first batch than Phuket, Krabi or
Pattaya. Current Muslim-owned restaurant evidence around Khao Lak is thinner,
so data quality takes priority over hitting a fixed candidate count.

## Batch 1

`database/seeds/phang_nga_expansion_review_queue.csv` contains **10
candidates**:

- 5 mosques covering Khao Lak/Takua Pa, Natai/Thai Mueang, Phang Nga Town,
  Ko Panyee and Ko Yao Noi,
- 3 Muslim/halal-oriented restaurants with current public listings,
- 2 accommodations with explicit halal-dining support.

## Restaurant trust

The three restaurant candidates remain `MUSLIM_FRIENDLY`, not
`MUSLIM_OWNED`, because the reviewed current sources describe Muslim/halal
food but do not explicitly establish Muslim ownership.

Do not infer ownership from names or cuisine.

## Excluded disputed listing

“Flavours Of India Halal Restaurant” is intentionally excluded from Batch 1.
A July 2026 traveller report disputes both Muslim ownership and the halal claim,
and the reviewed current evidence does not resolve that conflict. A halal word
in a listing name is not sufficient for Vela Muslim Travel.

## Accommodation trust

- The Sarojin: official website states halal dietary requirements can be
  accommodated. It is `MUSLIM_FRIENDLY`, not certified.
- Casa de La Flora: current Muslim-travel directory lists halal dining on
  request and Muslim-friendly facilities. It remains `MUSLIM_FRIENDLY`.

## Coordinate policy

No candidate receives inferred coordinates.

## Next expansion

Continue with **Trang**.
