import pytest

from app import routing
from app.routing import RouteResult, RoutingError, _coordinate_path
from app.schemas import Coordinate


@pytest.fixture(autouse=True)
def clear_route_cache() -> None:
    routing._route_cache.clear()


def test_routing_error_is_runtime_error() -> None:
    assert issubclass(RoutingError, RuntimeError)


def test_coordinate_path_supports_via_points() -> None:
    points = [
        Coordinate(latitude=8.1, longitude=99.6),
        Coordinate(latitude=11.8, longitude=99.9),
        Coordinate(latitude=14.5, longitude=101.3),
    ]

    assert _coordinate_path(points) == "99.6,8.1;99.9,11.8;101.3,14.5"


def test_coordinate_path_requires_model_valid_coordinates() -> None:
    with pytest.raises(ValueError):
        Coordinate(latitude=100.0, longitude=99.6)


@pytest.mark.asyncio
async def test_route_result_is_cached(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    async def fake_fetch(points: list[Coordinate]) -> RouteResult:
        nonlocal calls
        calls += 1
        return RouteResult(
            coordinates=[
                [points[0].longitude, points[0].latitude],
                [points[-1].longitude, points[-1].latitude],
            ],
            distance_m=1000,
            duration_s=120,
        )

    monkeypatch.setattr(routing.settings, "routing_provider", "osrm")
    monkeypatch.setattr(routing, "_fetch_osrm", fake_fetch)

    origin = Coordinate(latitude=8.1, longitude=99.6)
    destination = Coordinate(latitude=14.5, longitude=101.3)

    first = await routing.get_route(origin, destination)
    second = await routing.get_route(origin, destination)

    assert calls == 1
    assert first is second


@pytest.mark.asyncio
async def test_route_via_uses_distinct_cache_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    async def fake_fetch(points: list[Coordinate]) -> RouteResult:
        nonlocal calls
        calls += 1
        return RouteResult(
            coordinates=[
                [point.longitude, point.latitude]
                for point in points
            ],
            distance_m=1000 * len(points),
            duration_s=120 * len(points),
        )

    monkeypatch.setattr(routing.settings, "routing_provider", "osrm")
    monkeypatch.setattr(routing, "_fetch_osrm", fake_fetch)

    origin = Coordinate(latitude=8.1, longitude=99.6)
    stop = Coordinate(latitude=11.8, longitude=99.9)
    destination = Coordinate(latitude=14.5, longitude=101.3)

    await routing.get_route(origin, destination)
    await routing.get_route_via(origin, stop, destination)

    assert calls == 2
