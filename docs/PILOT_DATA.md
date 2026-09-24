# Pilot Data Workflow

## Why discovery data is separate from production data

Real-world Muslim travel data is trust-sensitive. A place can be publicly described as halal without having a current official certificate, and accommodation claims can be even less precise.

For that reason, Phase 0 separates:

1. **Synthetic fixtures** — safe for engineering tests only.
2. **Discovery candidates** — real places collected from public sources but not yet approved for production.
3. **Verified production places** — reviewed records with coordinates, evidence, status and freshness.

## Current pilot file

`database/seeds/pilot_places.csv` contains the first discovery candidates.

A candidate must not be imported into production merely because it appears in this file.

## Promotion checklist

Before a discovery candidate becomes a production listing:

- confirm the place still exists,
- resolve exact coordinates,
- confirm category,
- confirm current phone/address where practical,
- inspect the evidence behind Muslim/halal claims,
- use `HALAL_CERTIFIED` only with traceable official certification evidence,
- otherwise use the most accurate non-certified status,
- record source reference,
- record date checked,
- record expiry when certification has one,
- retain reviewer/admin notes.

## Accommodation rule

Accommodation is not automatically "halal certified" because:

- halal food is available,
- it is close to a mosque,
- Muslim guests recommend it,
- the owner is Muslim.

Those are separate facts and should be stored separately.

## Pilot geography

The first useful corridor should cover a real long-distance drive rather than random nationwide pins. Initial discovery work is focused on the northbound southern corridor through Phetchaburi/Bangkok toward the Khao Yai region.

## Next data task

Build a controlled geocoding/import step that:

1. reads discovery candidates,
2. resolves coordinates,
3. requires a human review state,
4. writes approved places and verification evidence,
5. rejects duplicate or ambiguous locations.
