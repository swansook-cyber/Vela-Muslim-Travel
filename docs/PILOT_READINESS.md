# Pilot Readiness Gate

The pilot corridor is intentionally narrow before nationwide expansion:

- นครศรีธรรมราช
- ชุมพร
- เพชรบุรี
- นครราชสีมา

Run:

```bash
cd apps/api
python -m app.tools.pilot_readiness
```

The command reads **production places only** and ignores synthetic
`TEST_FIXTURE` rows.

It returns a non-zero exit code when any target province has zero active
production places. The report also shows category gaps for restaurant, mosque
and accommodation coverage.

This is a minimum readiness gate, not a quality score. A province having one
place does not mean coverage is sufficient; route smoke testing and field/use
validation still come next.
