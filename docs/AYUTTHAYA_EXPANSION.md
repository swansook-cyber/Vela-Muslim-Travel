# Ayutthaya Expansion Batch 1

Checkpoint: 2026-09-26

Ayutthaya is the eighth tourism expansion dataset.

## Coverage

`database/seeds/ayutthaya_expansion_review_queue.csv` contains **13 candidates**:

- 5 mosques around the historic city and Muslim communities,
- 5 restaurants,
- 3 accommodations.

## Muslim-owned restaurants

Krua Muslim Krung Kao and Hatyai Fried Chicken Muhammad are stored as
`MUSLIM_OWNED` because current SalamXP checked listings explicitly identify
Muslim ownership / Muslim kitchen operation.

Other Muslim/halal restaurant listings remain `MUSLIM_FRIENDLY` when the
reviewed source does not explicitly establish ownership.

## Accommodations

Vanida Halal Resort, sala ayutthaya and RUS Hotel & Convention are stored as
`MUSLIM_FRIENDLY`.

Vanida is supported by current accommodation data plus an operating company
record for VANIDA HALAL RESORT CO., LTD.; this does not substitute for a current
official halal certificate number.

sala ayutthaya and RUS currently expose halal breakfast/dietary options, but
both may also serve alcohol. The label therefore describes Muslim-friendly
food availability, not a fully halal property.

## Holds

Krua Muslim Krung Kao and RUS Hotel require exact street-address reconciliation
before approval.

## Coordinate policy

No coordinates are inferred from text addresses.

## Next expansion

Continue with **Kanchanaburi**.
