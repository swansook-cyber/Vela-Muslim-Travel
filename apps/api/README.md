# API

Phase 0 backend: FastAPI + PostgreSQL/PostGIS.

## Implemented endpoints

- `GET /health`
- `POST /places/nearby`
- `POST /routes/along`

The Along My Route endpoint gets a drivable route from the configured routing provider, then uses PostGIS to find places inside the selected corridor and sorts them by route progress.

## Local development

From the repository root:

```bash
docker compose up -d db
```

Then:

```bash
cd apps/api
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

On Windows, copy `.env.example` to `.env` manually or use:

```powershell
Copy-Item .env.example .env
```

OpenAPI docs are available at `/docs`.

## Example Near Me request

```json
{
  "latitude": 13.7563,
  "longitude": 100.5018,
  "radius_m": 5000,
  "place_types": ["RESTAURANT", "MOSQUE"],
  "limit": 50
}
```

## Example Along My Route request

```json
{
  "origin": {
    "latitude": 8.1646,
    "longitude": 99.6804
  },
  "destination": {
    "latitude": 14.5289,
    "longitude": 101.3722
  },
  "corridor_radius_m": 5000,
  "place_types": [
    "RESTAURANT",
    "ACCOMMODATION",
    "MOSQUE",
    "PRAYER_ROOM"
  ],
  "limit": 100
}
```

## Routing provider note

The default Phase 0 adapter uses the public OSRM demo endpoint for development only. It is not a production SLA service. The adapter boundary exists so a production routing provider or self-hosted router can replace it without changing the database model.

## Data integrity

The API returns the most recent verification record for each place. A listing must not be promoted to a certified status without traceable evidence.


## Candidate staging

Discovery candidates can be validated without entering production:

```bash
python -m app.tools.import_candidates ../../database/seeds/pilot_candidates_review_queue.csv
```

To stage them in Postgres:

```bash
python -m app.tools.import_candidates ../../database/seeds/pilot_candidates_review_queue.csv --apply
```

The default mode is dry-run.

## Admin review API

Admin endpoints are disabled until `ADMIN_API_KEY` is configured.

When enabled, requests must send `X-Admin-Key`.

Available Phase 0 admin operations:

- `GET /admin/candidates`
- `PATCH /admin/candidates/{candidate_id}`
- `POST /admin/candidates/{candidate_id}/promote`

Do not put the admin key in the public PWA.
