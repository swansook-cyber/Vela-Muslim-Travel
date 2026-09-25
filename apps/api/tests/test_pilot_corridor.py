from app.tools.pilot_readiness import PILOT_PROVINCES


def test_pilot_corridor_covers_key_northbound_provinces() -> None:
    assert PILOT_PROVINCES == (
        "นครศรีธรรมราช",
        "สุราษฎร์ธานี",
        "ชุมพร",
        "ประจวบคีรีขันธ์",
        "เพชรบุรี",
        "สระบุรี",
        "นครราชสีมา",
    )
