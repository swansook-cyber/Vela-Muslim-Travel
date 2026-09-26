# Bangkok Expansion Batch 1

Checkpoint: 2026-09-26

Bangkok is the first city expansion outside the seven-province pilot corridor.

## Goal

Build useful Muslim-travel coverage gradually without making Google Places API
a mandatory discovery source.

The discovery hierarchy for this batch is:

1. official/public Muslim institution sources,
2. official business/hotel websites,
3. secondary public cross-checks,
4. Google Place ID / Google Places only as an optional coordinate fallback.

No candidate in this batch receives inferred coordinates.

## Starter set

`database/seeds/bangkok_expansion_review_queue.csv` contains **9 new
candidates**:

- 5 mosques from the CICOT mosque directory,
- 3 Muslim-friendly accommodations from their official websites,
- 1 restaurant from the official Al Meroz dining page.

The existing **Sophia Restaurant (Halal)** candidate already in
`pilot_candidates_review_queue.csv` brings the practical Bangkok starter set
to **10 places**.

## Trust policy

The hotels/restaurants may describe halal-certified dining or Muslim-friendly
facilities on their own official websites. Until a current official
certification record and certificate number are attached, these candidates
remain `MUSLIM_FRIENDLY`, not `HALAL_CERTIFIED`.

Mosques are sourced from the CICOT mosque directory but stay `UNVERIFIED` in
the generic trust field because that field is primarily used for commercial
halal/travel claims.


## Muslim-owned discovery rule

For restaurants and accommodations, actively include businesses that can be
credibly verified as **Muslim-owned**, even if they have never applied for a
halal certificate.

Use:

- `MUSLIM_OWNED` when ownership is verified,
- `MUSLIM_FRIENDLY` when the venue explicitly supports Muslim travelers but
  Muslim ownership is not established,
- `HALAL_CERTIFIED` / `HALAL_CERTIFIED_SERVICE` only with current official
  certification evidence.

A Muslim-owned business should not be excluded merely because it lacks an
official certificate. At the same time, Muslim ownership must not be inferred
from a name, logo, neighborhood or menu alone.

## Coordinate policy

Coordinates remain blank until one of these is available:

- direct embedded map coordinates from the source,
- a reliable public map/Plus Code that can be cross-checked,
- controlled manual geocoding,
- optional Google Place-ID resolver.

Do not approximate coordinates from the text address.

## Next cities

After Bangkok review/import quality is accepted, continue one city/province at a
time, prioritizing:

1. Phuket
2. Krabi
3. Chiang Mai
4. Chonburi / Pattaya
5. Songkhla / Hat Yai
6. Phang Nga
7. Trang
8. Ayutthaya
9. Kanchanaburi
