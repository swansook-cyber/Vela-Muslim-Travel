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
- Google-resolvable review filtering and queue shortcut,
- promotion preflight for duplicate proximity and production slug conflicts,
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
- production Docker Compose full-stack smoke tests,
- real-route coverage summaries plus a 2/5/10 km pilot smoke matrix,
- canonical Phase 0 completion dashboard with blocker-driven quick actions,
- guarded final Phase 0 acceptance recorded in the Admin audit log,
- first-usable PWA result cards with full address, trust provenance, evidence
  freshness, external navigation, website/social links, and empty-result guidance.

The code path for closing Phase 0 is now in place. The remaining gate is real data work: complete manual coordinate review for the curated pilot candidates, resolve recorded holds, promote only approved records, then run the 2/5/10 km end-to-end route smoke from southern Thailand toward Khao Yai. When those checks pass, Admin can record Final Phase 0 Acceptance and the Completion panel changes to **PHASE 0 COMPLETE**.


## Pilot review status

The discovery seed currently contains **24 curated candidates total**: **23 candidates across the seven target corridor provinces** plus **1 Bangkok candidate outside the route corridor**. The candidate-coverage gate verifies the seven pilot provinces:

- at least one restaurant in every target province,
- at least one mosque in every target province,
- accommodation candidates in at least two target provinces.

A first public-source cross-check pass has now been recorded for all **23 corridor candidates** in `docs/PILOT_REVIEW_LOG.md`.

**Coordinate-review checkpoint (2026-09-26): 15/23 corridor candidates are GEOCODED and 8 remain DISCOVERED.** The Admin workflow can now resolve Google-backed candidates directly from their stored Place IDs, singly or as a capped read-only batch. Returned coordinates remain draft suggestions until a reviewer opens the map and explicitly records `coordinate_checked_at`.

The public pilot is still **not** production-ready: the remaining coordinate review, resolution of flagged evidence/address/phone/closure discrepancies, duplicate checks, approval, and promotion are required before listings can appear in route results.

Admin now exposes a **Google Fast Lane** for Google-resolvable pilot candidates without manual holds, a **Phase 0 Completion** summary, and a guarded **Accept Phase 0** action. Final acceptance cannot be recorded until the mechanical gate is clear and the manual route-smoke checklist is confirmed.


## Closing Phase 0

Use `docs/RELEASE_READINESS.md` as the single execution checklist from the
current pilot checkpoint to `PHASE 0 COMPLETE`. It intentionally freezes
unrelated feature expansion until data review, promotion, route QA and deploy
verification are finished.


## City expansion

Bangkok expansion has started with a separate review seed:
`database/seeds/bangkok_expansion_review_queue.csv`.

Batch 1 adds 9 new Bangkok candidates (5 mosques, 3 accommodations, 1
restaurant). Together with the existing Sophia Restaurant candidate, the
Bangkok starter set is 10 places. Google Places is optional for coordinates,
not the primary discovery source.

See `docs/BANGKOK_EXPANSION.md`.


### Phuket Batch 1

Phuket expansion is available at
`database/seeds/phuket_expansion_review_queue.csv`.

Batch 1 contains 13 candidates: 5 mosques, 5 explicitly Muslim-owned
restaurants, and 3 Muslim-friendly accommodations. All remain review candidates
with blank coordinates until map verification is completed.

See `docs/PHUKET_EXPANSION.md`.


### Krabi Batch 1

Krabi expansion is available at
`database/seeds/krabi_expansion_review_queue.csv`.

Batch 1 contains 13 candidates: 5 mosques, 5 Muslim-owned restaurants, and 3
accommodations. Aonang Silver Orchid Resort is explicitly Muslim-owned from its
official website; the other accommodation trust labels remain conservative.

See `docs/KRABI_EXPANSION.md`.


### Chiang Mai Batch 1

Chiang Mai expansion is available at
`database/seeds/chiang_mai_expansion_review_queue.csv`.

Batch 1 contains 13 candidates: 5 mosques, 5 Muslim-owned restaurants, and 3
accommodations. Al-Farooq Hotel is held for current-operation confirmation
rather than being treated as active automatically.

See `docs/CHIANG_MAI_EXPANSION.md`.


### Chonburi / Pattaya Batch 1

Chonburi / Pattaya expansion is available at
`database/seeds/chonburi_pattaya_expansion_review_queue.csv`.

Batch 1 contains 13 candidates: 5 mosques, 5 Muslim-owned restaurants and 3
accommodations. Hard Rock Hotel Pattaya uses a current official
`HALAL_CERTIFIED_SERVICE` record for its restaurant kitchen only.

See `docs/CHONBURI_PATTAYA_EXPANSION.md`.


### Songkhla / Hat Yai Batch 1

Songkhla / Hat Yai expansion is available at
`database/seeds/songkhla_hat_yai_expansion_review_queue.csv`.

Batch 1 contains 13 candidates: 5 mosques, 5 Muslim-owned restaurants and 3
Muslim-friendly accommodations.

See `docs/SONGKHLA_HAT_YAI_EXPANSION.md`.


### Phang Nga Batch 1

Phang Nga expansion is available at
`database/seeds/phang_nga_expansion_review_queue.csv`.

Batch 1 deliberately contains 10 higher-confidence candidates rather than
forcing a fixed batch size. A disputed “halal” restaurant listing was excluded
because current evidence does not support the claim safely.

See `docs/PHANG_NGA_EXPANSION.md`.


### Trang Batch 1

Trang expansion is available at
`database/seeds/trang_expansion_review_queue.csv`.

Batch 1 contains 11 candidates: 5 mosques, 4 Muslim-friendly restaurants and 2
Muslim-friendly accommodations. Muslim ownership is not inferred where the
current source does not explicitly establish it.

See `docs/TRANG_EXPANSION.md`.


### Ayutthaya Batch 1

Ayutthaya expansion is available at
`database/seeds/ayutthaya_expansion_review_queue.csv`.

Batch 1 contains 13 candidates: 5 mosques, 5 restaurants and 3
Muslim-friendly accommodations. Muslim-owned status is used only for two
restaurants with explicit ownership evidence.

See `docs/AYUTTHAYA_EXPANSION.md`.


### Kanchanaburi Batch 1

Kanchanaburi expansion is available at
`database/seeds/kanchanaburi_expansion_review_queue.csv`.

Batch 1 contains 10 higher-confidence candidates: 5 mosques, 4
Muslim-friendly restaurants and 1 Muslim-friendly accommodation.

See `docs/KANCHANABURI_EXPANSION.md`.


### Surat Thani / Koh Samui Batch 1

Surat Thani / Koh Samui expansion is available at
`database/seeds/surat_thani_koh_samui_expansion_review_queue.csv`.

Batch 1 contains 10 candidates: 5 mosques, 2 restaurants and 3
Muslim-friendly accommodations. All remain review candidates with blank
coordinates until map verification is completed.

See `docs/SURAT_THANI_KOH_SAMUI_EXPANSION.md`.


### Chiang Rai Batch 1

Chiang Rai expansion is available at
`database/seeds/chiang_rai_expansion_review_queue.csv`.

Batch 1 contains 10 candidates: 5 mosques, 3 Muslim-owned restaurants and
2 Muslim-friendly accommodations. All remain review candidates with blank
coordinates until map verification is completed.

See `docs/CHIANG_RAI_EXPANSION.md`.
