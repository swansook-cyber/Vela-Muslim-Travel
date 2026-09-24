# Place Candidate Pipeline

## Purpose

Nationwide coverage cannot be built safely by inserting every search result directly into the production `places` table.

`place_candidates` is the staging area for discovery and evidence review.

## States

### DISCOVERED

A real-world candidate has been found from an official directory, business listing, field report or public source.

It may have no coordinates yet and must not appear in production route results.

### GEOCODED

Coordinates have been resolved and checked for obvious ambiguity.

This still does not mean the Muslim/halal claim is verified.

### APPROVED

An admin has reviewed:

- identity,
- coordinates,
- category,
- trust label,
- evidence,
- certification expiry where applicable.

Only then should the record be promoted to `places` and `place_verifications`.

### REJECTED

Duplicate, closed, wrong location, insufficient evidence, or otherwise unsuitable.

## Certification rule

A certificate for a restaurant or kitchen service does not automatically certify an entire hotel.

Examples:

- restaurant certificate → `HALAL_CERTIFIED`
- hotel kitchen / food service certificate → accommodation may carry `HALAL_CERTIFIED_SERVICE`
- whole property must not be shown as halal-certified unless evidence explicitly supports that claim.

## External identifiers

Store provider identifiers in staging when available. They help with:

- deduplication,
- later coordinate review,
- matching updated business records.

They are supporting identifiers, not halal evidence.

## Current pilot queue

`database/seeds/pilot_candidates_review_queue.csv` intentionally contains candidates that are not yet production records. It includes official evidence where available but leaves coordinate promotion to a controlled review step.
