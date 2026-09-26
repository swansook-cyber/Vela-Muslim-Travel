from app.admin_schemas import PilotReadinessResponse
from app.tools.pilot_readiness import ProvinceReadiness, readiness_passes


def test_admin_pilot_readiness_model_shape() -> None:
    items = [
        ProvinceReadiness("นครศรีธรรมราช", 1, 1, 1),
        ProvinceReadiness("ชุมพร", 1, 1, 1),
        ProvinceReadiness("เพชรบุรี", 1, 1, 0),
        ProvinceReadiness("นครราชสีมา", 1, 1, 0),
    ]

    assert readiness_passes(items)
    assert items[2].missing_types == ["ACCOMMODATION"]

    response = PilotReadinessResponse(
        ready=True,
        accommodation_provinces=2,
        provinces=[],
    )

    assert response.accommodation_provinces == 2
    assert response.required_accommodation_provinces == 2
