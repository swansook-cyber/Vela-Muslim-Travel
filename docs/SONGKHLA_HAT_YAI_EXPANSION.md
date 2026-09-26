# Songkhla / Hat Yai Expansion Batch 1

Checkpoint: 2026-09-26

Songkhla / Hat Yai is the sixth major tourism expansion dataset.

## Coverage strategy

Prioritize practical travel zones:

- central Hat Yai,
- Khlong Hae,
- routes toward Hat Yai Airport,
- Mueang Songkhla.

## Batch 1

`database/seeds/songkhla_hat_yai_expansion_review_queue.csv` contains **13
candidates**:

- 5 mosques from the CICOT Songkhla directory,
- 5 restaurants with explicit current Muslim-owned evidence,
- 3 Muslim-friendly accommodations.

All candidates begin as `DISCOVERED` with blank coordinates.

## Muslim-owned restaurants

Kai Tod Decha, Chabura Dimsum, Salma Halal Restaurant, Hamid Restaurant and
Dapor Muslim are stored as `MUSLIM_OWNED` only where current Muslim travel
sources explicitly identify Muslim ownership/operation.

No restaurant is upgraded to `HALAL_CERTIFIED` without a current official
certificate number.

## Accommodations

Alfahad Hotel, Hatyai Paradise Hotel and Yannaty Hotel all have current evidence
of halal dining or Muslim-oriented accommodation services.

They remain `MUSLIM_FRIENDLY` in this batch because no current official
certificate number/scope is attached to the seed.

## Coordinate policy

No coordinate is inferred from an address. Use controlled source-map review,
reliable Plus Codes/direct coordinates, or optional Google Place-ID resolution.

## Next expansion

Continue with **Phang Nga**.
