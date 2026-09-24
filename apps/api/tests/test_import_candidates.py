import pytest

from app.tools.import_candidates import parse_candidate


def candidate_row() -> dict[str, str]:
    return {
        "name": "Example",
        "place_type": "RESTAURANT",
        "address": "Example address",
        "district": "Example district",
        "province": "Bangkok",
        "phone": "",
        "proposed_trust_status": "UNVERIFIED",
        "source_type": "PUBLIC_WEB_SOURCE",
        "source_reference": "https://example.com",
        "external_provider": "example",
        "external_id": "example-1",
        "certification_number": "",
        "certification_expires_at": "",
        "review_state": "DISCOVERED",
        "review_note": "",
    }


def test_candidate_parses_discovery_row() -> None:
    candidate = parse_candidate(candidate_row(), 2)
    assert candidate.review_state == "DISCOVERED"
    assert candidate.proposed_trust_status == "UNVERIFIED"


def test_certified_candidate_requires_certificate_number() -> None:
    row = candidate_row()
    row["proposed_trust_status"] = "HALAL_CERTIFIED"
    row["source_type"] = "OFFICIAL_CERTIFICATION"

    with pytest.raises(ValueError, match="certification_number"):
        parse_candidate(row, 2)


def test_accommodation_certified_service_is_allowed() -> None:
    row = candidate_row()
    row["place_type"] = "ACCOMMODATION"
    row["proposed_trust_status"] = "HALAL_CERTIFIED_SERVICE"
    row["source_type"] = "OFFICIAL_CERTIFICATION"
    row["certification_number"] = "TEST-123"
    row["certification_expires_at"] = "2026-12-31T23:59:59+07:00"

    candidate = parse_candidate(row, 2)
    assert candidate.certification_number == "TEST-123"


def test_accommodation_whole_property_certified_label_is_rejected() -> None:
    row = candidate_row()
    row["place_type"] = "ACCOMMODATION"
    row["proposed_trust_status"] = "HALAL_CERTIFIED"
    row["source_type"] = "OFFICIAL_CERTIFICATION"
    row["certification_number"] = "TEST-123"

    with pytest.raises(ValueError, match="HALAL_CERTIFIED_SERVICE"):
        parse_candidate(row, 2)
