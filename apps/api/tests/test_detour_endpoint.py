from fastapi.testclient import TestClient

from app import main
from app.routing import RouteResult


def test_detour_endpoint_returns_added_time(monkeypatch) -> None:
    async def fake_route_via(origin, stop, destination):
        return RouteResult(
            coordinates=[
                [origin.longitude, origin.latitude],
                [stop.longitude, stop.latitude],
                [destination.longitude, destination.latitude],
            ],
            distance_m=110_000,
            duration_s=7_200,
        )

    monkeypatch.setattr(main, "get_route_via", fake_route_via)

    client = TestClient(main.app)
    response = client.post(
        "/routes/detour",
        json={
            "origin": {"latitude": 8.1, "longitude": 99.6},
            "stop": {"latitude": 11.8, "longitude": 99.9},
            "destination": {"latitude": 14.5, "longitude": 101.3},
            "base_distance_m": 100000,
            "base_duration_s": 6000,
        },
    )

    assert response.status_code == 200
    assert response.json()["added_distance_m"] == 10000
    assert response.json()["added_duration_s"] == 1200


def test_detour_endpoint_clamps_negative_delta(monkeypatch) -> None:
    async def fake_route_via(origin, stop, destination):
        return RouteResult(
            coordinates=[
                [origin.longitude, origin.latitude],
                [stop.longitude, stop.latitude],
                [destination.longitude, destination.latitude],
            ],
            distance_m=90_000,
            duration_s=5_500,
        )

    monkeypatch.setattr(main, "get_route_via", fake_route_via)

    client = TestClient(main.app)
    response = client.post(
        "/routes/detour",
        json={
            "origin": {"latitude": 8.1, "longitude": 99.6},
            "stop": {"latitude": 11.8, "longitude": 99.9},
            "destination": {"latitude": 14.5, "longitude": 101.3},
            "base_distance_m": 100000,
            "base_duration_s": 6000,
        },
    )

    assert response.status_code == 200
    assert response.json()["added_distance_m"] == 0
    assert response.json()["added_duration_s"] == 0
