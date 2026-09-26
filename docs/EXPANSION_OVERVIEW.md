# Tourism Expansion Overview

Checkpoint: 2026-09-26

Wave 1 expands Vela Muslim Travel beyond the original seven-province route
pilot into major tourism cities/provinces using separate review queues.

These are **candidate records**, not production places. Every record still
requires the normal review / coordinate / approval / promotion workflow.

## Wave 1 totals

| Expansion | New candidates | Mosques | Restaurants | Accommodations |
| --- | ---: | ---: | ---: | ---: |
| Bangkok | 9 | 5 | 1 | 3 |
| Phuket | 13 | 5 | 5 | 3 |
| Krabi | 13 | 5 | 5 | 3 |
| Chiang Mai | 13 | 5 | 5 | 3 |
| Chonburi / Pattaya | 13 | 5 | 5 | 3 |
| Songkhla / Hat Yai | 13 | 5 | 5 | 3 |
| Phang Nga | 10 | 5 | 3 | 2 |
| Trang | 11 | 5 | 4 | 2 |
| Ayutthaya | 13 | 5 | 5 | 3 |
| Kanchanaburi | 10 | 5 | 4 | 1 |
| **Wave 1 total** | **118** | **50** | **42** | **26** |

Together with the original 24-record pilot seed, the repository now contains
**142 curated review records** across the base pilot plus Wave 1 expansion
files. This is a review-data count, not a count of approved/promoted production
places.

## Commercial trust mix

Across the 68 restaurant/accommodation candidates in Wave 1:

- **29** are `MUSLIM_OWNED` from explicit ownership/operation evidence,
- **38** are `MUSLIM_FRIENDLY`,
- **1** is `HALAL_CERTIFIED_SERVICE` with an official current certificate at
  review time (Hard Rock Hotel Pattaya restaurant-kitchen scope).

The 50 mosque candidates remain `UNVERIFIED` in the generic commercial trust
field; their mosque identity comes from CICOT directory evidence.

## Review holds

Wave 1 intentionally keeps narrow holds where evidence is incomplete:

1. **Al-Farooq Hotel Chiang Mai** — confirm current operation.
2. **Muslim Seafood Restaurant, Pattaya** — reconcile locality wording.
3. **Trang Oasis Waterpark Hotel** — verify exact street address.
4. **Krua Muslim Krung Kao Ayutthaya** — verify exact street address.
5. **RUS Hotel & Convention Ayutthaya** — verify exact street address.
6. **Sanctuary Kanchanaburi** — verify exact street address.

A hold does not mean the place is rejected; it prevents approval until the
specific issue is resolved.

## Data-quality rules used in Wave 1

- Never infer Muslim ownership from a name, logo, menu or neighborhood.
- `MUSLIM_OWNED` requires explicit ownership/operation evidence.
- A “halal” word in a listing name is not enough to claim certification.
- Hotel halal breakfast/dining can support `MUSLIM_FRIENDLY`, but not
  whole-property halal certification.
- Certification labels require current official evidence and certificate scope.
- Coordinates are left blank unless they come from a controlled, reviewable
  source.
- Fixed batch size is less important than evidence quality.

## Wave 2 priority

After Wave 1 import/CI quality is stable, continue with tourism areas that add
meaningful geographic coverage:

1. Surat Thani / Koh Samui (deeper tourism expansion beyond the route pilot)
2. Chiang Rai
3. Rayong
4. Trat / Koh Chang
5. Satun / Koh Lipe
6. Nakhon Pathom
7. Ratchaburi
8. Sukhothai / Phitsanulok

Each province should use its own review seed and the same trust rules.
