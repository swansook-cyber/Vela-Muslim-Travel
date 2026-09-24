# Phase 0 Acceptance

Phase 0 is complete only when the data and route engine are proven, not merely scaffolded.

## Automated gates

GitHub Actions must pass:

- Ruff lint
- unit tests
- PostGIS schema initialization
- synthetic seed loading
- Near Me spatial filtering
- place-type filtering
- Along My Route corridor filtering
- Along My Route travel-order sorting

## Data safety gates

- Synthetic fixtures are clearly marked and never production listings.
- Discovery candidates are not imported automatically.
- Only APPROVED rows can be imported.
- Certified statuses require OFFICIAL_CERTIFICATION plus a source reference.
- A source and verification timestamp are retained with trust-sensitive claims.

## Route-engine gates

- Route provider is replaceable behind an adapter.
- Database stores places independently of the route provider.
- Straight-line distance to route is treated separately from road detour time.
- Production ranking may later use actual detour time for shortlisted candidates.

## What Phase 0 does not prove yet

- nationwide place coverage
- production-grade routing SLA
- booking integrations
- real-time opening hours
- public crowdsourcing
- polished web/PWA UX
- production deployment

## Exit criterion

Once CI is green and a manually reviewed real-world pilot dataset returns sensible results on a real Thailand route, development can move to the first usable PWA.
