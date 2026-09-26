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

Before the pilot can be considered structurally ready in production data:

- every target corridor province has at least one restaurant,
- every target corridor province has at least one mosque,
- accommodation coverage exists in at least two target provinces,
- reviewed/promoted production places return sensible results on the real southern-Thailand → Khao Yai route,
- the 2/5/10 km route smoke matrix has been inspected for practical detour coverage.

This structural gate is necessary but not sufficient by itself. Manual route acceptance
must still confirm that the returned stops are useful, correctly ordered, evidence-backed,
and practical for a real drive.

Once CI is green and this manually reviewed real-world pilot returns sensible route results,
development can move to the first usable PWA.
