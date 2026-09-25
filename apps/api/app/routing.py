import asyncio
import time
from dataclasses import dataclass

import httpx

from .config import get_settings
from .schemas import Coordinate

settings = get_settings()


@dataclass(slots=True)
class RouteResult:
    coordinates: list[list[float]]
    distance_m: float
    duration_s: float


class RoutingError(RuntimeError):
    pass


_route_cache: dict[str, tuple[float, RouteResult]] = {}
_provider_lock = asyncio.Lock()
_last_provider_request_at = 0.0


def _coordinate_path(points: list[Coordinate]) -> str:
    return ";".join(
        f"{point.longitude},{point.latitude}"
        for point in points
    )


def _cache_key(points: list[Coordinate]) -> str:
    return _coordinate_path(points)


def _get_cached(key: str) -> RouteResult | None:
    cached = _route_cache.get(key)
    if cached is None:
        return None

    expires_at, result = cached
    if expires_at <= time.monotonic():
        _route_cache.pop(key, None)
        return None

    return result


def _set_cached(key: str, result: RouteResult) -> None:
    if len(_route_cache) >= settings.routing_cache_max_entries:
        oldest_key = min(_route_cache, key=lambda item: _route_cache[item][0])
        _route_cache.pop(oldest_key, None)

    _route_cache[key] = (
        time.monotonic() + settings.routing_cache_ttl_seconds,
        result,
    )


async def _fetch_osrm(points: list[Coordinate]) -> RouteResult:
    global _last_provider_request_at

    coordinates = _coordinate_path(points)
    url = f"{settings.osrm_base_url.rstrip('/')}/route/v1/driving/{coordinates}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "false",
    }
    headers = {
        "User-Agent": settings.routing_user_agent,
        "Accept": "application/json",
    }

    async with _provider_lock:
        elapsed = time.monotonic() - _last_provider_request_at
        delay = settings.routing_min_interval_seconds - elapsed
        if delay > 0:
            await asyncio.sleep(delay)

        async with httpx.AsyncClient(
            timeout=settings.route_request_timeout_seconds,
            headers=headers,
        ) as client:
            response = await client.get(url, params=params)

        _last_provider_request_at = time.monotonic()

    if response.status_code != 200:
        raise RoutingError(f"Routing provider returned HTTP {response.status_code}")

    payload = response.json()
    routes = payload.get("routes") or []
    if payload.get("code") != "Ok" or not routes:
        raise RoutingError(payload.get("message") or "No drivable route found")

    route = routes[0]
    geometry = route.get("geometry") or {}
    route_coordinates = geometry.get("coordinates") or []

    if len(route_coordinates) < 2:
        raise RoutingError("Routing provider returned an invalid route geometry")

    return RouteResult(
        coordinates=route_coordinates,
        distance_m=float(route["distance"]),
        duration_s=float(route["duration"]),
    )


async def get_route_through(points: list[Coordinate]) -> RouteResult:
    if len(points) < 2:
        raise RoutingError("At least two routing points are required")

    if settings.routing_provider.lower() != "osrm":
        raise RoutingError(f"Unsupported routing provider: {settings.routing_provider}")

    key = _cache_key(points)
    cached = _get_cached(key)
    if cached is not None:
        return cached

    result = await _fetch_osrm(points)
    _set_cached(key, result)
    return result


async def get_route(origin: Coordinate, destination: Coordinate) -> RouteResult:
    return await get_route_through([origin, destination])


async def get_route_via(
    origin: Coordinate,
    stop: Coordinate,
    destination: Coordinate,
) -> RouteResult:
    return await get_route_through([origin, stop, destination])
