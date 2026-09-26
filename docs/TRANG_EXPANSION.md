# Trang Expansion Batch 1

Checkpoint: 2026-09-26

Trang is the seventh tourism expansion dataset.

## Coverage

`database/seeds/trang_expansion_review_queue.csv` contains **11 candidates**:

- 5 mosques covering Mueang Trang, Kantang, Ko Muk and Ko Libong,
- 4 active Muslim/halal-oriented restaurants,
- 2 accommodations with property-level halal breakfast/service evidence.

## Trust policy

The reviewed restaurant sources identify Muslim/halal food but do not explicitly
establish Muslim ownership. They therefore remain `MUSLIM_FRIENDLY`, not
`MUSLIM_OWNED`.

Trang Oasis Waterpark Hotel and Rabiang Lay Ko Libong Homestay both have current
property-level evidence of halal breakfast/service, but no ownership or official
certification number is attached.

## Address hold

Trang Oasis Waterpark Hotel carries a narrow address-verification hold because
the reviewed current property data confirms Palian/Trang and halal service but
does not expose a complete street address in the captured source. Do not approve
until the exact property address is reconciled.

## Coordinate policy

No coordinate is approximated from a text address.

## Next expansion

Continue with **Ayutthaya**.
