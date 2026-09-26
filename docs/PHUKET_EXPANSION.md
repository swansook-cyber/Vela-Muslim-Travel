# Phuket Expansion Batch 1

Checkpoint: 2026-09-26

Phuket is the second city/province expansion after Bangkok.

## Coverage strategy

Prioritize the tourism zones where Muslim travelers are most likely to need
useful nearby data:

- Patong,
- Bang Tao / Choeng Thale,
- Kamala,
- Phuket Town / Ko Kaeo,
- Rawai.

## Batch 1

`database/seeds/phuket_expansion_review_queue.csv` contains **13 candidates**:

- 5 mosques sourced from the CICOT mosque directory,
- 5 restaurants explicitly identified by current public sources as
  **Muslim-owned**,
- 3 accommodations whose official/current sources show Muslim-friendly or
  halal dining support.

All candidates start as `DISCOVERED` with blank coordinates.

## Muslim-owned policy

The five restaurant candidates are labeled `MUSLIM_OWNED` because the source
explicitly identifies Muslim ownership.

This does not mean `HALAL_CERTIFIED`.

Do not upgrade a restaurant to `HALAL_CERTIFIED` unless a current official
certificate record and certificate number are attached.

## Accommodation policy

Andaman Beach Hotel, Bangtao Beach Chalet and Harmony Patong Hotel are stored as
`MUSLIM_FRIENDLY`.

Their sources describe halal-certified kitchens, halal restaurants, halal food
or Muslim-friendly facilities, but Batch 1 does not attach a current official
certificate number/scope. Therefore the property itself must not be presented
as fully halal-certified.

## Coordinate policy

No candidate receives inferred coordinates.

Use, in order:

1. direct embedded-map coordinates from the source,
2. reliable current public map / Plus Code,
3. controlled geocoding and visual review,
4. optional Google Place-ID resolver.

## Next expansion

After Phuket Batch 1 review quality is accepted, continue with **Krabi** using
the same trust and coordinate rules.
