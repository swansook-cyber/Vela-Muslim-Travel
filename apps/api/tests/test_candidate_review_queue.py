import pytest
from fastapi import HTTPException

from app import main
from app.admin_schemas import (
    CandidateCoordinateBatchRequest,
    CandidateReviewState,
    CandidateReviewUpdate,
)


def candidate_row(state: str) -> dict:
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "ร้านทดสอบ",
        "place_type": "RESTAURANT",
        "address": "ปากช่อง",
        "district": "ปากช่อง",
        "province": "นครราชสีมา",
        "phone": None,
        "latitude": 14.7,
        "longitude": 101.4,
        "proposed_trust_status": "UNVERIFIED",
        "source_type": "PUBLIC_WEB_SOURCE",
        "source_reference": "https://example.com/place",
        "external_provider": None,
        "external_id": None,
        "certification_number": None,
        "certification_expires_at": None,
        "review_state": state,
        "review_note": None,
        "review_hold_reason": None,
        "source_checked_at": now,
        "coordinate_checked_at": now,
        "created_at": now,
        "updated_at": now,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "state",
    [CandidateReviewState.DISCOVERED, CandidateReviewState.GEOCODED],
)
async def test_review_queue_supports_manual_review_states(monkeypatch, state) -> None:
    seen: dict[str, object] = {}

    async def fake_list_candidates(
        session,
        review_state,
        province=None,
        place_type=None,
        limit=100,
    ):
        seen["review_state"] = review_state
        seen["province"] = province
        seen["place_type"] = place_type
        seen["limit"] = limit
        return [candidate_row(state.value)]

    monkeypatch.setattr(main, "list_candidates", fake_list_candidates)

    tasks = await main.admin_candidate_review_queue(
        session=None,
        _admin=None,
        review_state=state,
        province="นครราชสีมา",
        place_type=None,
        limit=100,
    )

    assert seen["review_state"] == state
    assert tasks[0].review_state == state
    assert tasks[0].ready_to_approve is True
    assert tasks[0].approval_blockers == []
    assert tasks[0].maps_search_url.startswith(
        "https://www.google.com/maps/search/?api=1&query="
    )


@pytest.mark.asyncio
async def test_review_queue_rejects_non_review_state() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await main.admin_candidate_review_queue(
            session=None,
            _admin=None,
            review_state=CandidateReviewState.APPROVED,
            province=None,
            place_type=None,
            limit=100,
        )

    assert exc_info.value.status_code == 422
    assert "DISCOVERED or GEOCODED" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_review_queue_uses_exact_google_place_id(monkeypatch) -> None:
    row = candidate_row(CandidateReviewState.DISCOVERED.value)
    row["external_provider"] = "google_business"
    row["external_id"] = "ChIJexactQueue123"

    async def fake_list_candidates(
        session,
        review_state,
        province=None,
        place_type=None,
        limit=100,
    ):
        return [row]

    monkeypatch.setattr(main, "list_candidates", fake_list_candidates)

    tasks = await main.admin_candidate_review_queue(
        session=None,
        _admin=None,
        review_state=CandidateReviewState.DISCOVERED,
        province="นครราชสีมา",
        place_type=None,
        limit=100,
    )

    assert "query=" in tasks[0].maps_search_url
    assert "query_place_id=ChIJexactQueue123" in tasks[0].maps_search_url


@pytest.mark.asyncio
async def test_batch_google_resolver_returns_per_candidate_results(monkeypatch) -> None:
    rows = {
        "google-ok": {
            **candidate_row(CandidateReviewState.DISCOVERED.value),
            "id": "google-ok",
            "external_provider": "google_business",
            "external_id": "ChIJok",
        },
        "not-google": {
            **candidate_row(CandidateReviewState.DISCOVERED.value),
            "id": "not-google",
            "external_provider": "makan_halal_guide",
            "external_id": "123",
        },
    }

    async def fake_get_candidate(session, candidate_id):
        return rows.get(candidate_id)

    class Result:
        place_id = "ChIJok"
        latitude = 14.1234567
        longitude = 101.7654321

    async def fake_resolve_google_place_location(place_id):
        assert place_id == "ChIJok"
        return Result()

    monkeypatch.setattr(main.settings, "google_places_api_key", "test-key")
    monkeypatch.setattr(main, "get_candidate", fake_get_candidate)
    monkeypatch.setattr(
        main,
        "resolve_google_place_location",
        fake_resolve_google_place_location,
    )

    response = await main.admin_resolve_candidate_google_places(
        request=CandidateCoordinateBatchRequest(
            candidate_ids=["google-ok", "missing", "not-google"],
        ),
        session=None,
        _admin=None,
    )

    assert len(response.results) == 3
    assert response.results[0].suggestion is not None
    assert response.results[0].suggestion.external_id == "ChIJok"
    assert response.results[0].suggestion.latitude == pytest.approx(14.1234567)
    assert response.results[1].error == "Candidate not found"
    assert response.results[2].error == (
        "Candidate does not use a Google place provider"
    )


@pytest.mark.asyncio
async def test_batch_google_resolver_requires_configuration(monkeypatch) -> None:
    monkeypatch.setattr(main.settings, "google_places_api_key", None)

    with pytest.raises(HTTPException) as exc_info:
        await main.admin_resolve_candidate_google_places(
            request=CandidateCoordinateBatchRequest(candidate_ids=["candidate-1"]),
            session=None,
            _admin=None,
        )

    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_candidate_update_rejects_discovered_to_approved_jump(monkeypatch) -> None:
    row = candidate_row(CandidateReviewState.DISCOVERED.value)

    async def fake_get_candidate(session, candidate_id):
        assert candidate_id == row["id"]
        return row

    monkeypatch.setattr(main, "get_candidate", fake_get_candidate)

    with pytest.raises(HTTPException) as exc_info:
        await main.admin_update_candidate(
            candidate_id=row["id"],
            update=CandidateReviewUpdate(
                review_state=CandidateReviewState.APPROVED,
            ),
            session=None,
            _admin=None,
        )

    assert exc_info.value.status_code == 409
    assert "DISCOVERED -> APPROVED" in str(exc_info.value.detail)
