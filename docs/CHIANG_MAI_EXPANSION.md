# Chiang Mai Expansion Batch 1

Checkpoint: 2026-09-26

Chiang Mai is the fourth expansion dataset after Bangkok, Phuket and Krabi.

## Current context

Chiang Mai launched the provincial **Chiang Mai Muslim Friendly 2026** program
with the provincial tourism association, Islamic committee and public agencies.
The program includes halal food promotion and Muslim-friendly tourism
development.

## Batch 1

`database/seeds/chiang_mai_expansion_review_queue.csv` contains **13
candidates**:

- 5 mosques from the CICOT mosque directory,
- 5 explicitly Muslim-owned restaurants,
- 3 accommodations.

All candidates start as `DISCOVERED` with blank coordinates.

## Muslim-owned restaurants

Tai Restaurant, Khao Soi Islam, Ruammit II, Gulf Restaurant and Ruammit 1 are
stored as `MUSLIM_OWNED` only where the reviewed source explicitly says so.

Do not upgrade to `HALAL_CERTIFIED` without current official certificate
evidence.

## Accommodations

- Casa Marocc: `MUSLIM_FRIENDLY`; current sources show halal breakfast/use by
  Muslim travelers, but the official property site does not establish Muslim
  ownership.
- Romena Grand: `MUSLIM_FRIENDLY`; current booking/hotel sources show halal
  dining.
- Al-Farooq Hotel: `MUSLIM_OWNED` from a current directory description as a
  Muslim hotel, but it carries an explicit operation-status hold because online
  reservations are currently disabled.

## Coordinate policy

No coordinate is approximated from text addresses.

Use direct embedded maps, reliable Plus Codes/current map sources, controlled
geocoding with review, or optional Google Place-ID resolution.

## Next expansion

After Chiang Mai Batch 1 passes import/review quality checks, continue with
**Chonburi / Pattaya**.
