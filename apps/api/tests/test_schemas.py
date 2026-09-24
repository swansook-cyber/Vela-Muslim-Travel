import pytest
from pydantic import ValidationError

from app.schemas import AlongRouteRequest, Coordinate, NearbyRequest


def test_nearby_rejects_invalid_radius() -> None:
    with pytest.raises(ValidationError):
        NearbyRequest(latitude=13.7, longitude=100.5, radius_m=99)


def test_coordinate_rejects_invalid_latitude() -> None:
    with pytest.raises(ValidationError):
        Coordinate(latitude=91, longitude=100)


def test_along_route_defaults_to_five_km_corridor() -> None:
    request = AlongRouteRequest(
        origin=Coordinate(latitude=8.16, longitude=99.68),
        destination=Coordinate(latitude=14.53, longitude=101.37),
    )

    assert request.corridor_radius_m == 5000
