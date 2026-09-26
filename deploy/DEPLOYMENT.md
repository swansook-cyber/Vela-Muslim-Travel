# Production Deployment

## Preconditions

- Docker Engine + Docker Compose plugin
- a private `.env` based on `deploy/.env.example`
- a long random PostgreSQL password
- a separate long random Admin API key
- HTTPS termination in front of the web container
- optional Google Places API key if Admin should resolve stored Google Place IDs
  into coordinate suggestions

## Preflight

Before starting production, validate the private environment file:

```bash
python3 deploy/preflight.py deploy/.env
```

The preflight fails on default/short database credentials, missing Admin key,
non-HTTPS production CORS origins, or `ALLOW_TEST_FIXTURES=true`. It warns
when Google Places is disabled and when the pilot still depends on public
OSRM/Nominatim services.

## Start

```bash
docker compose --env-file deploy/.env -f docker-compose.prod.yml up -d --build
```

The stack starts in this order:

1. PostGIS becomes healthy.
2. API runs pending database migrations and starts FastAPI.
3. API health check must pass.
4. Web/nginx starts and proxies `/api/` to FastAPI.

## Check

```bash
docker compose --env-file deploy/.env -f docker-compose.prod.yml ps
curl -fsS http://127.0.0.1:8080/api/health
```

## Backup

Run before upgrades that can affect persistent data:

```bash
BACKUP_DIR=/srv/backups/vela-muslim-travel ./deploy/backup-db.sh
```

The backup uses PostgreSQL custom format (`pg_dump -Fc`).

## Restore safety

Database restore replaces data and is intentionally not automated here.
A restore should only be performed after explicitly selecting the backup,
target database, and downtime window.

## Upgrade

1. create a database backup,
2. pull the new Git commit,
3. run `python3 deploy/preflight.py deploy/.env`,
4. inspect pending migration files,
5. rebuild and restart Compose,
6. verify `/api/health`,
7. verify the web UI, Admin dashboard, and Phase 0 Completion panel.

The API container applies ordered SQL migrations before serving traffic.

## Optional Google Places resolver

Set `GOOGLE_PLACES_API_KEY` in the private deploy environment only when the
Admin Place ID resolver is needed. Keep it blank to disable that feature.
The key is passed only to the API container and is never compiled into the web
client. Coordinate lookup is a reviewer aid only; it does not automatically
verify, approve, or promote a candidate.
