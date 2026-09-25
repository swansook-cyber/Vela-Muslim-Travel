# Routing Provider Operations

The development default uses the public OSRM demo endpoint. It is suitable for
proof-of-concept and low-volume validation only; it is not a production SLA.

The routing adapter therefore includes basic protection:

- identifying User-Agent,
- small in-memory route cache,
- configurable minimum interval between provider requests,
- serialized provider access inside one API process,
- on-demand detour calculation rather than calculating detours for every result.

Configuration:

- `ROUTING_CACHE_TTL_SECONDS`
- `ROUTING_CACHE_MAX_ENTRIES`
- `ROUTING_MIN_INTERVAL_SECONDS`
- `ROUTING_USER_AGENT`

For public production traffic, replace the demo endpoint with a routing service
whose capacity and terms match the deployment, or self-host the routing engine.
The application code remains provider-isolated behind `app.routing`.
