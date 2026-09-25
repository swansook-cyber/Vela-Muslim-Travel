# Synthetic Fixture Isolation

Synthetic Phase 0 places are marked with `source_status = TEST_FIXTURE`.

Public place queries hide them by default. This protects production from
accidentally exposing synthetic restaurants, accommodation or mosques if a test
seed is ever loaded into a persistent database.

`ALLOW_TEST_FIXTURES=true` is used only by the PostGIS integration test job so
the route and nearby query tests can exercise known synthetic geometry.

Production environment files explicitly keep this setting false.
