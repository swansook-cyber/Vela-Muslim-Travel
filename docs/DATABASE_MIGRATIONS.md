# Database Migrations

The production database uses a persistent PostGIS volume, so changing
`database/schema.sql` does not update an already-created database.

Vela Muslim Travel therefore uses a small ordered SQL migration runner.

## Rules

- `database/schema.sql` remains the canonical fresh-install schema.
- Incremental production changes go in `apps/api/migrations/`.
- Migration filenames are ordered, for example:
  - `0001_baseline.sql`
  - `0002_add_place_field.sql`
- The API container runs migrations before Uvicorn starts.
- Applied versions are stored in `schema_migrations`.
- Migrations must be safe to run once and should be written transactionally.

## Development

With the database running:

```bash
cd apps/api
python -m app.migrations
```

GitHub Actions runs the migration runner against a real PostGIS service and
checks that a second run is idempotent.

## Deployment safety

Do not make destructive schema changes in an automatic migration without an
explicit backup and rollback plan.
