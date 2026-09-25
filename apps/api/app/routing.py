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


def _coordinate_path(points: list[Coordinate]) -> str:
    return ";".join(
        f"{point.longitude},{point.latitude}"
        for point in points
    )


async def get_route_through(points: list[Coordinate]) -> RouteResult:
    if len(points) < 2:
        raise RoutingError("At least two routing points are required")

    if settings.routing_provider.lower() != "osrm":
        raise RoutingError(f"Unsupported routing provider: {settings.routing_provider}")

    coordinates = _coordinate_path(points)
    url = f"{settings.osrm_base_url.rstrip('/')}/route/v1/driving/{coordinates}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "false",
    }

    async with httpx.AsyncClient(timeout=settings.route_request_timeout_seconds) as client:
        response = await client.get(url, params=params)

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


async def get_route(origin: Coordinate, destination: Coordinate) -> RouteResult:
    return await get_route_through([origin, destination])


async def get_route_via(
    origin: Coordinate,
    stop: Coordinate,
    destination: Coordinate,
) -> RouteResult:
    return await get_route_through([origin, stop, destination])
