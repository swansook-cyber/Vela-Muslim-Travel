# Kanchanaburi Expansion Batch 1

Checkpoint: 2026-09-26

Kanchanaburi closes the first tourism-city expansion sequence.

## Coverage

`database/seeds/kanchanaburi_expansion_review_queue.csv` contains **10
candidates**:

- 5 mosques covering Mueang Kanchanaburi, Tha Muang, Tha Maka, Sai Yok and
  Sangkhla Buri,
- 4 active Muslim/halal-oriented restaurants in Mueang Kanchanaburi,
- 1 accommodation with explicit property-level halal dining evidence.

## Restaurant trust

Dawood Cha, Kismi Roti, Halal Kitchen (Bang Kalis) and Amin remain
`MUSLIM_FRIENDLY` because the current reviewed source identifies
Muslim/halal food but does not explicitly establish Muslim ownership.

## Accommodation trust

Sanctuary Kanchanaburi currently lists halal breakfast and halal dietary options
at its own restaurant. It is stored as `MUSLIM_FRIENDLY`, not certified.

Good Times Resort and Baan Apa Erawan Resort are intentionally not included as
Muslim-friendly accommodations merely because halal food is available nearby;
nearby food is not a property-level service claim.

## Hold

Sanctuary Kanchanaburi requires exact street-address reconciliation before
approval.

## Coordinate policy

No coordinates are inferred from addresses.
