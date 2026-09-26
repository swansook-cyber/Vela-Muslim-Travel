from datetime import UTC, datetime, timedelta

from app.candidate_review import (
    candidate_approval_blockers,
    candidate_maps_search_url,
    candidate_promotion_blockers,
    candidate_review_transition_allowed,
    candidate_review_warnings,
)


def base_candidate() -> dict:
    return {
        "name": "ร้านทดสอบ",
        "address": "อำเภอปากช่อง",
        "district": "ปากช่อง",
        "province": "นครราชสีมา",
        "latitude": 14.7,
        "longitude": 101.4,
        "proposed_trust_status": "UNVERIFIED",
        "source_type": "PUBLIC_WEB_SOURCE",
        "source_reference": "https://example.com/place",
        "certification_number": None,
        "certification_expires_at": None,
        "review_hold_reason": None,
        "source_checked_at": datetime.now(UTC),
        "coordinate_checked_at": datetime.now(UTC),
    }


def test_candidate_maps_search_url_contains_encoded_query() -> None:
    url = candidate_maps_search_url(base_candidate())
    assert url.startswith("https://www.google.com/maps/search/?api=1&query=")
    assert "%E0%B8" in url


def test_candidate_approval_requires_coordinates() -> None:
    candidate = base_candidate()
    candidate["latitude"] = None
    candidate["longitude"] = None

    blockers = candidate_approval_blockers(candidate)

    assert "reviewed coordinates are required" in blockers


def test_candidate_approval_requires_provenance() -> None:
    candidate = base_candidate()
    candidate["source_reference"] = None

    blockers = candidate_approval_blockers(candidate)

    assert "source reference is required" in blockers


def test_certified_candidate_requires_current_official_evidence() -> None:
    candidate = base_candidate()
    candidate.update(
        {
            "proposed_trust_status": "HALAL_CERTIFIED",
            "source_type": "OFFICIAL_CERTIFICATION",
            "certification_number": "TEST-1",
            "certification_expires_at": datetime.now(UTC) + timedelta(days=30),
        }
    )

    assert candidate_approval_blockers(candidate) == []


def test_expired_certified_candidate_is_blocked() -> None:
    candidate = base_candidate()
    candidate.update(
        {
            "proposed_trust_status": "HALAL_CERTIFIED",
            "source_type": "OFFICIAL_CERTIFICATION",
            "certification_number": "TEST-1",
            "certification_expires_at": datetime.now(UTC) - timedelta(days=1),
        }
    )

    blockers = candidate_approval_blockers(candidate)

    assert any("non-expired" in item for item in blockers)


def test_candidate_approval_is_blocked_by_manual_review_hold() -> None:
    candidate = base_candidate()
    candidate["review_hold_reason"] = "Confirm reopening before approval"

    blockers = candidate_approval_blockers(candidate)

    assert blockers == [
        "manual review hold: Confirm reopening before approval"
    ]


def test_candidate_approval_requires_source_cross_check_date() -> None:
    candidate = base_candidate()
    candidate["source_checked_at"] = None

    blockers = candidate_approval_blockers(candidate)

    assert "source cross-check date is required" in blockers


def test_candidate_approval_requires_coordinate_verification_date() -> None:
    candidate = base_candidate()
    candidate["coordinate_checked_at"] = None

    blockers = candidate_approval_blockers(candidate)

    assert "coordinate verification date is required" in blockers


def test_candidate_maps_search_prefers_google_place_id() -> None:
    candidate = base_candidate()
    candidate["external_provider"] = "google_business"
    candidate["external_id"] = "ChIJexact123"

    url = candidate_maps_search_url(candidate)

    assert "query=" in url
    assert "query_place_id=ChIJexact123" in url


def test_candidate_maps_search_falls_back_to_name_and_address() -> None:
    candidate = base_candidate()
    candidate["external_provider"] = "public_directory"
    candidate["external_id"] = None

    url = candidate_maps_search_url(candidate)

    assert "query_place_id=" not in url
    assert "query=" in url


def test_candidate_review_transition_requires_geocoded_before_approved() -> None:
    assert candidate_review_transition_allowed("DISCOVERED", "GEOCODED") is True
    assert candidate_review_transition_allowed("GEOCODED", "APPROVED") is True
    assert candidate_review_transition_allowed("DISCOVERED", "APPROVED") is False


def test_candidate_review_transition_allows_remediation_and_reopen() -> None:
    assert candidate_review_transition_allowed("APPROVED", "GEOCODED") is True
    assert candidate_review_transition_allowed("APPROVED", "REJECTED") is True
    assert candidate_review_transition_allowed("REJECTED", "DISCOVERED") is True
    assert candidate_review_transition_allowed("PROMOTED", "GEOCODED") is False


def test_candidate_review_warns_when_certification_expires_within_30_days() -> None:
    candidate = base_candidate()
    candidate.update(
        {
            "proposed_trust_status": "HALAL_CERTIFIED",
            "source_type": "OFFICIAL_CERTIFICATION",
            "certification_number": "TEST-SOON",
            "certification_expires_at": datetime.now(UTC) + timedelta(days=10),
        }
    )

    warnings = candidate_review_warnings(candidate)

    assert len(warnings) == 1
    assert "expires within 30 days" in warnings[0]


def test_candidate_review_does_not_warn_for_distant_certification_expiry() -> None:
    candidate = base_candidate()
    candidate.update(
        {
            "proposed_trust_status": "HALAL_CERTIFIED",
            "source_type": "OFFICIAL_CERTIFICATION",
            "certification_number": "TEST-LATER",
            "certification_expires_at": datetime.now(UTC) + timedelta(days=60),
        }
    )

    assert candidate_review_warnings(candidate) == []


def test_candidate_promotion_blockers_reject_expired_certificate() -> None:
    candidate = base_candidate()
    candidate.update(
        {
            "review_state": "APPROVED",
            "proposed_trust_status": "HALAL_CERTIFIED",
            "certification_expires_at": datetime.now(UTC) - timedelta(days=1),
        }
    )

    assert candidate_promotion_blockers(candidate) == [
        "certified candidate requires current non-expired certificate"
    ]


def test_candidate_promotion_blockers_accept_current_approved_candidate() -> None:
    candidate = base_candidate()
    candidate.update(
        {
            "review_state": "APPROVED",
            "proposed_trust_status": "HALAL_CERTIFIED",
            "certification_expires_at": datetime.now(UTC) + timedelta(days=30),
        }
    )

    assert candidate_promotion_blockers(candidate) == []
