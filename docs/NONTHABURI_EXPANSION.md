# Nonthaburi Expansion Batch 1

Checkpoint: 2026-09-26

Nonthaburi follows Samut Prakan and extends the Bangkok metropolitan coverage
north and northwest.

## Batch 1

`database/seeds/nonthaburi_expansion_review_queue.csv` contains **11
candidates**:

- 5 current CICOT mosque records,
- 3 active Muslim/Halal restaurant candidates,
- 3 accommodation candidates with explicit current halal dining evidence.

All candidates begin as `DISCOVERED` with blank coordinates.

## Mosque coverage

CICOT currently lists many Nonthaburi mosques. Batch 1 samples Mueang
Nonthaburi, Pak Kret and Bang Bua Thong, including Tha It Mosque and Darussalam
Central Mosque.

This is not a complete provincial mosque inventory.

## Restaurant evidence

Current Wongnai data supports Muna Roti Tea Coffee Nonthaburi, MUMTAS and Halal
Oven as active Muslim/Halal venues. These remain `MUSLIM_FRIENDLY` unless
explicit Muslim ownership or a current official certificate is attached.

## Accommodation evidence

- Bed By Cruise Hotel At Samakkhi-Tivanont: Booking states the restaurant serves
  halal options.
- Bed in Beyt Boutique Hotel: Booking lists halal dietary options.
- Regent Ngamwongwan Hotel: Agoda explicitly describes a dedicated halal
  restaurant.

These are service-level Muslim-friendly signals, not whole-property halal
certification.

## Coordinate policy

Coordinates remain blank until controlled map review or an approved resolver
provides verifiable location evidence.

## Next expansion

After Nonthaburi passes import/review quality checks, continue with
**Pathum Thani**.
