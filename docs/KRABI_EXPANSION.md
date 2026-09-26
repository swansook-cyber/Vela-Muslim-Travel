# Krabi Expansion Batch 1

Checkpoint: 2026-09-26

Krabi is the third expansion dataset after Bangkok and Phuket.

## Coverage strategy

Prioritize the areas most useful to Muslim travelers:

- Krabi Town / Sai Thai,
- Ao Nang / Nopparat Thara,
- Nong Thale / Klong Muang,
- Railay / Ao Nam Mao,
- Ko Phi Phi,
- Ko Lanta.

## Batch 1

`database/seeds/krabi_expansion_review_queue.csv` contains **13 candidates**:

- 5 mosques from the CICOT directory,
- 5 restaurants with explicit current Muslim-owned evidence,
- 3 accommodations with Muslim-owned or Muslim-friendly evidence.

All begin as `DISCOVERED` with blank coordinates.

## Muslim-owned accommodation

Aonang Silver Orchid Resort is stored as `MUSLIM_OWNED` because its own
official website states that it is locally owned by a Muslim family and provides
a 100% halal food environment.

This still does not make the entire property `HALAL_CERTIFIED`. A current
official certificate number and scope would be required for a certification
label.

## Restaurant trust

Basmati, Ocean Hill Krabi, Chill Lay Lanta, May & Zin, and Kuan Nom Saow are
stored as `MUSLIM_OWNED` only where the reviewed public source explicitly
describes Muslim ownership/family operation.

Do not infer Muslim ownership from names, staff appearance, neighborhood, or
menu alone.

## Muslim-friendly hotels

Krabi Front Bay Resort and Railay Princess Resort & Spa are stored as
`MUSLIM_FRIENDLY` from current hotel/halal-travel evidence.

Claims about halal kitchens or halal-friendly status are not upgraded to
`HALAL_CERTIFIED_SERVICE` unless a current official certificate number and
scope are attached.

## Coordinate policy

No candidate receives approximate coordinates from an address.

Coordinates must come from a direct embedded map, reliable Plus Code/current
map source, controlled geocoding with review, or optional Google Place-ID
resolver.

## Next expansion

After Krabi Batch 1 passes import/review quality checks, continue with
**Chiang Mai**.
