import pytest

from app.routing import RoutingError, _coordinate_path
from app.schemas import Coordinate


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
