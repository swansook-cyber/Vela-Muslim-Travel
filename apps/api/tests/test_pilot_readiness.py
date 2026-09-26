from app.tools.pilot_readiness import ProvinceReadiness, readiness_passes


def test_readiness_requires_restaurant_and_mosque_in_every_target_province() -> None:
    items = [
        ProvinceReadiness("A", 1, 1, 1),
        ProvinceReadiness("B", 1, 1, 1),
        ProvinceReadiness("C", 1, 1, 0),
    ]
    assert readiness_passes(items)


def test_readiness_fails_when_a_province_lacks_restaurant_or_mosque() -> None:
    items = [
        ProvinceReadiness("A", 1, 1, 1),
        ProvinceReadiness("B", 1, 0, 1),
    ]
    assert not readiness_passes(items)


def test_readiness_requires_accommodation_in_two_provinces() -> None:
    items = [
        ProvinceReadiness("A", 1, 1, 1),
        ProvinceReadiness("B", 1, 1, 0),
        ProvinceReadiness("C", 1, 1, 0),
    ]
    assert not readiness_passes(items)


def test_missing_types_reports_category_gaps() -> None:
    item = ProvinceReadiness("A", restaurants=1, mosques=0, accommodation=0)
    assert item.missing_types == ["MOSQUE", "ACCOMMODATION"]
