from app.tools.pilot_readiness import ProvinceReadiness, readiness_passes


def test_readiness_requires_every_target_province_to_have_a_place() -> None:
    items = [
        ProvinceReadiness("A", 1, 0, 0),
        ProvinceReadiness("B", 0, 1, 0),
        ProvinceReadiness("C", 0, 0, 1),
    ]
    assert readiness_passes(items)


def test_readiness_fails_when_a_province_is_empty() -> None:
    items = [
        ProvinceReadiness("A", 1, 0, 0),
        ProvinceReadiness("B", 0, 0, 0),
    ]
    assert not readiness_passes(items)


def test_missing_types_reports_category_gaps() -> None:
    item = ProvinceReadiness("A", restaurants=1, mosques=0, accommodation=0)
    assert item.missing_types == ["MOSQUE", "ACCOMMODATION"]
