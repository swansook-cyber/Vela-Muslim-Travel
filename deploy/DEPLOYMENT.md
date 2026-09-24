# Production Deployment

## Preconditions

- Docker Engine + Docker Compose plugin
- a private `.env` based on `deploy/.env.example`
- a long random PostgreSQL password
- a separate long random Admin API key
- HTTPS termination in front of the web container

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
3. inspect pending migration files,
4. rebuild and restart Compose,
5. verify `/api/health`,
6. verify the web UI and admin dashboard.

The API container applies ordered SQL migrations before serving traffic.
