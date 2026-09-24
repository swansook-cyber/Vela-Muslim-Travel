#!/usr/bin/env sh
set -eu

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT="${BACKUP_DIR}/vela-muslim-travel-${TIMESTAMP}.dump"

mkdir -p "${BACKUP_DIR}"

docker compose -f "${COMPOSE_FILE}" exec -T db   pg_dump -U vela -d vela_muslim_travel -Fc > "${OUTPUT}"

echo "Database backup created: ${OUTPUT}"
