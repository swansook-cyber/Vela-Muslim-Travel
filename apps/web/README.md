# Web / PWA

React + Vite + MapLibre client for Vela Muslim Travel.

## Current capabilities

- Near Me and Along My Route workflows,
- browser geolocation for origin,
- searchable origin and destination,
- configurable route corridor,
- filters for restaurant / accommodation / mosque / prayer room,
- MapLibre route rendering and result markers,
- route distance and duration summary,
- on-demand road detour calculation,
- trust status, verification source/date/expiry, and evidence links,
- full result address plus external Google Maps / Apple Maps navigation,
- website/social/phone actions when available,
- responsive layout,
- installable web manifest,
- service-worker shell caching with API/Admin data excluded from offline caching.

## Local development

Start the API first on port 8000.

Then:

```bash
cd apps/web
npm install
cp .env.example .env
npm run dev
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
npm run dev
```

The default API URL is:

```text
http://localhost:8000
```

Override it with `VITE_API_BASE_URL`.

## Map data

The Phase 0 map uses OpenStreetMap raster tiles with attribution. This is suitable for development and low-volume validation only. A production deployment must follow the OpenStreetMap tile usage policy or use an appropriate tile provider / self-hosted tile service.

## Remaining production caveats

The traveler workflow is usable for the pilot, but production readiness still
depends on reviewed/promoted real-world data and final route acceptance.

Restaurant `opening_hours` is currently stored as JSONB without a normalized
V1 schedule contract. The UI therefore does **not** infer a live open/closed
state yet; doing so before the hours format and timezone semantics are defined
would risk showing incorrect information.

The service worker intentionally caches only the application shell/static
assets. Route, place, verification and Admin data remain network-backed so
trust-sensitive information is not served stale from an offline cache.
