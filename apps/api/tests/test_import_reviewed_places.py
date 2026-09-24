import pytest

from app.tools.import_reviewed_places import parse_row


def base_row() -> dict[str, str]:
    return {
        "slug": "example",
        "name_th": "ร้านตัวอย่าง",
        "name_en": "Example",
        "place_type": "RESTAURANT",
        "latitude": "13.7",
        "longitude": "100.5",
        "review_state": "APPROVED",
        "trust_status": "UNVERIFIED",
        "source_type": "PUBLIC_WEB_SOURCE",
        "source_reference": "https://example.com",
    }


def test_non_approved_row_is_skipped() -> None:
    row = base_row()
    row["review_state"] = "DISCOVERY_ONLY"
    assert parse_row(row, 2) is None


def test_approved_row_is_parsed() -> None:
    place = parse_row(base_row(), 2)
    assert place is not None
    assert place.slug == "example"


def test_certified_status_requires_official_source() -> None:
    row = base_row()
    row["trust_status"] = "HALAL_CERTIFIED"

    with pytest.raises(ValueError, match="OFFICIAL_CERTIFICATION"):
        parse_row(row, 2)


def test_certified_status_accepts_official_evidence() -> None:
    row = base_row()
    row["trust_status"] = "HALAL_CERTIFIED"
    row["source_type"] = "OFFICIAL_CERTIFICATION"

    place = parse_row(row, 2)
    assert place is not None
    assert place.trust_status == "HALAL_CERTIFIED"
