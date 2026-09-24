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

- Web/PWA: React / Next.js
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
- candidate readiness dashboard,
- reviewed-coordinate preservation across candidate re-imports,
- verification-evidence guardrails and certificate-expiry handling,
- PostGIS integration tests in GitHub Actions,
- React + Vite + MapLibre route-search web client,
- browser geolocation for route origin,
- web and API CI pipelines,
- production Docker Compose full-stack smoke tests.

The next major gate is a manually reviewed real-world pilot dataset and an end-to-end route test using that data.
