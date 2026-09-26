# Samut Prakan Expansion Batch 1

Checkpoint: 2026-09-26

Samut Prakan follows Samut Songkhram / Amphawa and extends coverage into the
Bangkok metropolitan and Suvarnabhumi corridor.

## Batch 1

`database/seeds/samut_prakan_expansion_review_queue.csv` contains **11
candidates**:

- 5 mosques from the current CICOT directory,
- 3 active Muslim/Halal restaurant candidates,
- 3 accommodation candidates with explicit current halal dining/breakfast
  evidence.

All candidates begin as `DISCOVERED` with blank coordinates.

## Mosque coverage

CICOT currently lists many Samut Prakan mosques. Batch 1 deliberately samples
Mueang Samut Prakan, Phra Pradaeng, Bang Sao Thong and Bang Bo rather than
claiming to be a complete provincial inventory.

## Restaurant evidence

Anna Halal, Chamuss and Nai Noi Roti Hom all have current active Wongnai
listings with Muslim/Halal evidence. These remain `MUSLIM_FRIENDLY` unless
explicit Muslim ownership or a current official certificate is attached.

## Accommodation evidence

- Carnation Residence: Booking lists halal dietary options at the restaurant.
- The Bird Nest Homestay & Coffeeshop: Booking lists halal breakfast.
- NY City Resort And Spa: Agoda lists halal breakfast and a halal restaurant.

These are service-level Muslim-friendly signals, not whole-property halal
certification.

## Coordinate policy

Coordinates remain blank until controlled map review or an approved resolver
provides verifiable location evidence.

## Next expansion

After Samut Prakan passes import/review quality checks, continue with
**Nonthaburi**.
