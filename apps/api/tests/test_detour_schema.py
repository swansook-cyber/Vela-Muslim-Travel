import pytest

from app.schemas import DetourRequest


def test_detour_request_accepts_valid_trip() -> None:
    request = DetourRequest(
        origin={"latitude": 8.1, "longitude": 99.6},
        stop={"latitude": 11.8, "longitude": 99.9},
        destination={"latitude": 14.5, "longitude": 101.3},
        base_distance_m=700_000,
        base_duration_s=36_000,
    )

    assert request.stop.latitude == pytest.approx(11.8)


def test_detour_request_rejects_negative_base_duration() -> None:
    with pytest.raises(ValueError):
        DetourRequest(
            origin={"latitude": 8.1, "longitude": 99.6},
            stop={"latitude": 11.8, "longitude": 99.9},
            destination={"latitude": 14.5, "longitude": 101.3},
            base_distance_m=700_000,
            base_duration_s=-1,
        )
