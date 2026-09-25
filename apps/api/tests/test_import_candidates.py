from pathlib import Path

import pytest

from app.tools.import_candidates import load_candidates, parse_candidate


def candidate_row() -> dict[str, str]:
    return {
        "name": "Example",
        "place_type": "RESTAURANT",
        "address": "Example address",
        "district": "Example district",
        "province": "Bangkok",
        "phone": "",
        "latitude": "",
        "longitude": "",
        "proposed_trust_status": "UNVERIFIED",
        "source_type": "PUBLIC_WEB_SOURCE",
        "source_reference": "https://example.com",
        "external_provider": "example",
        "external_id": "example-1",
        "certification_number": "",
        "certification_expires_at": "",
        "review_state": "DISCOVERED",
        "review_note": "",
        "review_hold_reason": "",
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


def test_pilot_candidate_queue_is_valid() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(path)

    assert len(candidates) >= 24
    assert any(
        candidate.proposed_trust_status == "HALAL_CERTIFIED"
        for candidate in candidates
    )
    assert any(
        candidate.proposed_trust_status == "HALAL_CERTIFIED_SERVICE"
        for candidate in candidates
    )


def test_geocoded_candidate_requires_coordinates() -> None:
    row = candidate_row()
    row["review_state"] = "GEOCODED"

    with pytest.raises(ValueError, match="requires coordinates"):
        parse_candidate(row, 2)


def test_candidate_accepts_reviewed_coordinates() -> None:
    row = candidate_row()
    row["review_state"] = "GEOCODED"
    row["latitude"] = "14.529001"
    row["longitude"] = "101.372001"

    candidate = parse_candidate(row, 2)

    assert candidate.latitude == pytest.approx(14.529001)
    assert candidate.longitude == pytest.approx(101.372001)


def test_certified_candidate_requires_expiry() -> None:
    row = candidate_row()
    row["proposed_trust_status"] = "HALAL_CERTIFIED"
    row["source_type"] = "OFFICIAL_CERTIFICATION"
    row["certification_number"] = "TEST-123"

    with pytest.raises(ValueError, match="certification_expires_at"):
        parse_candidate(row, 2)


def test_candidate_requires_reference_for_known_source() -> None:
    row = candidate_row()
    row["source_reference"] = ""

    with pytest.raises(ValueError, match="requires source_reference"):
        parse_candidate(row, 2)


def test_unknown_source_may_omit_reference() -> None:
    row = candidate_row()
    row["source_type"] = "UNKNOWN"
    row["source_reference"] = ""

    candidate = parse_candidate(row, 2)
    assert candidate.source_reference is None


def test_candidate_parses_manual_review_hold() -> None:
    row = candidate_row()
    row["review_hold_reason"] = "Confirm current operating status"

    candidate = parse_candidate(row, 2)

    assert candidate.review_hold_reason == "Confirm current operating status"


def test_pilot_queue_contains_explicit_review_holds() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(path)

    held = [candidate for candidate in candidates if candidate.review_hold_reason]

    assert len(held) >= 7
    assert any("Temporarily Closed" in candidate.review_hold_reason for candidate in held)
