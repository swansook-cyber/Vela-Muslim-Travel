# Web / PWA

React + Vite + MapLibre client for Vela Muslim Travel.

## Current Phase 0 capabilities

- route-first search form,
- browser geolocation for origin,
- configurable route corridor,
- filters for restaurant / accommodation / mosque / prayer room,
- MapLibre route rendering,
- result markers,
- route distance and duration summary,
- trust-status display,
- responsive layout,
- installable web manifest baseline.

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

## Not production-ready yet

The current UI accepts destination coordinates. The product UX should later replace this with location search/autocomplete and saved/recent destinations.

Offline support is not complete yet. The manifest is only the installation baseline; service-worker and offline data behavior will be added after the core route workflow is validated.
