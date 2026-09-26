from app.tools.pilot_route_smoke import (
    PILOT_CORRIDORS_KM,
    PILOT_DESTINATION,
    PILOT_ORIGIN,
)


def test_pilot_route_smoke_uses_expected_corridors() -> None:
    assert PILOT_CORRIDORS_KM == (2, 5, 10)


def test_pilot_route_smoke_uses_south_to_khao_yai_endpoints() -> None:
    assert PILOT_ORIGIN.latitude == 8.16
    assert PILOT_ORIGIN.longitude == 99.68
    assert PILOT_DESTINATION.latitude == 14.53
    assert PILOT_DESTINATION.longitude == 101.37
