# Web Security Headers

The production nginx layer sends baseline browser security headers:

- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-Frame-Options: DENY`
- a restricted `Permissions-Policy`
- Content Security Policy limited to the application origin plus the current
  OpenStreetMap raster tile host.

MapLibre needs `blob:` workers, so the CSP explicitly permits workers from
`blob:`. The app does not permit arbitrary third-party scripts.

If the map tile provider changes later, update the CSP and smoke-test the map
before deployment.
