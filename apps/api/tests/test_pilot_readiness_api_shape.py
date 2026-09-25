from app.tools.pilot_readiness import ProvinceReadiness, readiness_passes


def test_admin_pilot_readiness_model_shape() -> None:
    items = [
        ProvinceReadiness("นครศรีธรรมราช", 1, 1, 0),
        ProvinceReadiness("ชุมพร", 1, 0, 0),
        ProvinceReadiness("เพชรบุรี", 1, 1, 0),
        ProvinceReadiness("นครราชสีมา", 1, 1, 0),
    ]

    assert readiness_passes(items)
    assert items[0].missing_types == ["ACCOMMODATION"]
