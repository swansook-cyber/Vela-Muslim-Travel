import pytest
from fastapi import HTTPException

from app import main
from app.admin_schemas import CandidateReviewState


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
