# Vela Muslim Travel

Travel companion for Muslim travelers in Thailand.

## Product goal

Help travelers answer practical questions while moving between destinations:

- Where can I eat halal or Muslim-owned food near me or along my route?
- Where can I stay at a Muslim-friendly or Muslim-owned accommodation?
- Where is the nearest mosque or prayer room?
- How far must I detour from my current route?
- How trustworthy and how recent is each listing?

## V1 scope

1. Restaurants
2. Accommodations
3. Mosques / prayer rooms
4. Near Me search
5. Along My Route search
6. Admin data maintenance
7. Verification provenance and last-verified date
8. Open external navigation in Google Maps / Apple Maps

Out of V1: social reviews, booking engine, prayer-time engine, qibla compass, complex user profiles, and nationwide crowdsourcing.

## Phase 0

Phase 0 proves the data model and route-search concept before investing in production UI.

- Define the core place schema.
- Seed a small travel corridor.
- Calculate places near a route using PostGIS.
- Rank results in travel order and by detour distance.
- Preserve verification source and freshness.

## Proposed architecture

- Web/PWA: React + Vite + MapLibre
- API: FastAPI
- Database: PostgreSQL + PostGIS
- Map: MapLibre
- Routing: pluggable routing provider initially; self-hosting can be evaluated later.

## Repository layout

```text
apps/
  web/
  api/
database/
  schema.sql
  seeds/
docs/
  PRODUCT_SCOPE.md
  DATA_MODEL.md
  ROUTE_POC.md
packages/
  shared/
```

## Data integrity principle

The application must not treat every Muslim-friendly listing as halal-certified.

Each place carries a clear status, verification source, and verification date. Certification claims must be distinguishable from owner-declared, community-reported, and unverified information.


## Current implementation status

Phase 0 now includes:

- FastAPI API with PostGIS spatial search,
- `Near Me` query,
- `Along My Route` query ordered by route progress,
- replaceable routing-provider adapter,
- controlled reviewed-place importer,
- controlled geocode candidate review with explicit coordinate selection,
- exact Google Place-ID coordinate suggestions with server-side caching,
- one-request batch coordinate suggestions for the filtered Admin queue,
- candidate readiness dashboard,
- reviewed-coordinate preservation across candidate re-imports,
- verification-evidence guardrails and certificate-expiry handling,
- PostGIS integration tests in GitHub Actions,
- React + Vite + MapLibre route-search web client,
- browser geolocation plus searchable trip origin/destination,
- on-demand road detour time and distance for route stops,
- candidate and production-place admin maintenance with audit history,
- pilot readiness reporting for the northbound Thailand corridor,
- PWA shell caching that excludes all API/admin responses,
- browser security headers and edge rate limits,
- web and API CI pipelines,
- production Docker Compose full-stack smoke tests.

The next major gate is completing manual coordinate review for the curated pilot candidates, promoting only approved records, and running an end-to-end route test from southern Thailand toward Khao Yai using production data.


## Pilot review status

The discovery seed currently contains **24 curated candidates total**: **23 candidates across the seven target corridor provinces** plus **1 Bangkok candidate outside the route corridor**. The candidate-coverage gate verifies the seven pilot provinces:

- at least one restaurant in every target province,
- at least one mosque in every target province,
- accommodation candidates in at least two target provinces.

A first public-source cross-check pass has now been recorded for all **23 corridor candidates** in `docs/PILOT_REVIEW_LOG.md`.

**Coordinate-review checkpoint (2026-09-26): 15/23 corridor candidates are GEOCODED and 8 remain DISCOVERED.** The Admin workflow can now resolve Google-backed candidates directly from their stored Place IDs, singly or as a capped read-only batch. Returned coordinates remain draft suggestions until a reviewer opens the map and explicitly records `coordinate_checked_at`.

The public pilot is still **not** production-ready: the remaining coordinate review, resolution of flagged evidence/address/phone/closure discrepancies, duplicate checks, approval, and promotion are required before listings can appear in route results.
