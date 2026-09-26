# Chonburi / Pattaya Expansion Batch 1

Checkpoint: 2026-09-26

Chonburi / Pattaya is the fifth expansion dataset after Bangkok, Phuket, Krabi
and Chiang Mai.

## Batch 1

`database/seeds/chonburi_pattaya_expansion_review_queue.csv` contains **13
candidates**:

- 5 mosques from the CICOT Chonburi directory,
- 5 restaurants with explicit Muslim-owned / Muslim-run evidence,
- 3 accommodations with halal-service or Muslim-friendly evidence.

All start as `DISCOVERED` with blank coordinates.

## Muslim-owned restaurants

Amir Halal Food, Khamis Zain, Ruchi, Afza and Muslim Seafood Restaurant are
stored as `MUSLIM_OWNED` only where the reviewed source explicitly identifies
Muslim ownership or operation.

Muslim Seafood Restaurant carries an address-reconciliation hold because the
current travel guide mixes Nong Prue with the wording “Amphoe Laem Chabang”.
Do not approve until the locality is reconciled.

## Accommodations

### Hard Rock Hotel Pattaya

Stored as `HALAL_CERTIFIED_SERVICE`, not whole-property certified.

Official Thailand Halal Information Center / CICOT evidence:

- certificate: `100J5760010662`
- brand/service: ZamZam at Starz Diner / halal restaurant kitchen
- status: Active at review time
- expiry: 2026-10-14

Re-check certificate validity immediately before promotion.

### Royal Cliff Hotels Group

Stored as `MUSLIM_FRIENDLY`.

The official hotel site states that its Halal Kitchen is HAL-Q certified by the
Halal Science Center, Chulalongkorn University, but this batch does not capture
a current certificate number. Do not upgrade to certified-service status yet.

### Centara Grand Mirage Beach Resort Pattaya

Stored as `MUSLIM_FRIENDLY`.

The official Centara site currently provides dedicated halal breakfast,
à-la-carte and in-room dining options. No current official certification number
is attached to this batch.

## Coordinate policy

No coordinates are approximated from addresses. Use controlled map review,
direct source maps/coordinates, reliable Plus Codes or optional Google
Place-ID resolution.

## Next expansion

Continue with **Songkhla / Hat Yai**.
