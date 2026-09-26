# Real Route Smoke Test

After reviewed candidates have been promoted into `places`, run the route smoke
tool against the same database used by the API.

Example:

```bash
cd apps/api
python -m app.tools.route_smoke \
  --origin-lat 8.16 \
  --origin-lng 99.68 \
  --destination-lat 14.53 \
  --destination-lng 101.37 \
  --corridor-km 5 \
  --require-core-types
```

The command prints:

- total route distance and duration from the configured routing provider,
- number of production places inside the route corridor,
- travel-order progress,
- distance from route,
- place type,
- current trust status,
- expired-evidence warning.

This command intentionally reads only promoted production places. Discovery
candidates are excluded until their coordinates and evidence are reviewed.


The summary also reports:

- counts by restaurant / mosque / prayer room / accommodation,
- number of represented provinces,
- expired verification evidence count,
- a **mechanical core coverage** check for food + prayer + accommodation.

`--require-core-types` exits non-zero if any of those three core needs is
missing. This is only a structural minimum; it does **not** mean the route is
useful enough for travelers. Manual acceptance must still inspect encounter
order, detour relevance, evidence quality, province gaps, and whether the
available stops are practical for a real drive.


## Pilot acceptance

For the initial Thailand pilot, repeat the smoke test with 2 km, 5 km and 10 km
corridors and confirm that:

1. results appear in encounter order,
2. irrelevant distant places are excluded,
3. trust labels match the evidence source,
4. expired certification evidence is visible,
5. restaurant, mosque/prayer and accommodation coverage is useful enough for a
   real drive before expanding nationwide.
