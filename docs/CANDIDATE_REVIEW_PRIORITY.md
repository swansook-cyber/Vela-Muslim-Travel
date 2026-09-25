# Candidate Review Priority

The Admin candidate list supports filtering by:

- review state,
- pilot province,
- place type.

Default ordering prioritizes the initial road corridor:

1. นครศรีธรรมราช
2. สุราษฎร์ธานี
3. ชุมพร
4. ประจวบคีรีขันธ์
5. เพชรบุรี
6. สระบุรี
7. นครราชสีมา

This keeps review work aligned with the route-first pilot instead of expanding
the directory nationwide before the core trip experience is proven.


## Current review milestone — 2026-09-25

The first public-source cross-check pass is complete for all **23 candidates**
inside the seven-province pilot corridor.

The seed file contains **24 candidates total**: 23 in the pilot corridor plus
one Bangkok candidate outside the corridor.

Cross-check completion does not move candidate state. The next gate is manual
coordinate verification in Admin:

1. open the source evidence,
2. compare current public identity/address/phone,
3. select a coordinate candidate,
4. visually verify the exact map location,
5. save as `GEOCODED`,
6. resolve any evidence, closure, address or phone discrepancy,
7. approve only after server blockers are clear.

Known review flags from the first pass are recorded in
`docs/PILOT_REVIEW_LOG.md`. In particular, temporary-closure or conflicting
address/phone evidence must be resolved rather than normalized automatically.
