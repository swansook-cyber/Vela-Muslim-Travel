# PWA Cache Safety

The service worker caches only the application shell and same-origin static
assets.

It deliberately does **not** cache `/api/` responses.

This is important because:

- admin API calls carry an `X-Admin-Key`,
- candidate review data is operational data,
- verification history can change,
- route/geocoding results can become stale.

Admin API responses also return `Cache-Control: no-store, private`.

Offline support therefore means the app shell can open without a network
connection; live travel/search/admin data still requires the API.
