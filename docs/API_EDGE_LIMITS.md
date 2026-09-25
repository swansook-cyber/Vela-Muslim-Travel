# Public API Edge Limits

The production nginx layer adds lightweight per-IP request limiting for the
external-provider-backed endpoints.

- geocoding: 1 request/second with a small burst
- routing and detour: 2 requests/second with a small burst
- oversized request bodies are rejected above 1 MiB

The limits protect the pilot from accidental rapid retries and reduce pressure
on external routing/geocoding providers. They are not a substitute for a
production-scale gateway if the service grows.

HTTP 429 means the client should wait before retrying.
