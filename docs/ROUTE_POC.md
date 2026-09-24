# Along My Route — Phase 0 POC

## Objective

Given an origin and destination, return Muslim-travel-relevant places close to the route in the order the traveler will encounter them.

## Inputs

- origin latitude/longitude
- destination latitude/longitude
- place types
- route corridor radius, e.g. 2 km / 5 km / 10 km
- optional trust-status filters

## Processing

1. Request a drivable route from the configured routing provider.
2. Decode the returned route polyline.
3. Convert it to a PostGIS LineString.
4. Find active places inside the requested route corridor.
5. For each place calculate:
   - straight-line distance to route,
   - fractional progress along the route using ST_LineLocatePoint,
   - approximate order encountered.
6. Optionally request detour travel time for a shortlist.
7. Return results ordered by route progress.

## Important distinction

"Distance from route" is not the same as "detour time".

Phase 0 may use route distance to shortlist candidates, but production ranking should be able to incorporate actual road detour time for the most relevant candidates.

## Acceptance criteria

A POC passes only if:

- places well outside the selected corridor are excluded,
- results appear in travel order,
- the same route works with restaurants, accommodations and mosques,
- verification status is returned with each result,
- the route provider can be swapped without changing database tables.

## First QA dataset

Start with a small set of manually checked places on one real travel corridor. Do not bulk-import thousands of unverified listings merely to make the map look populated.
