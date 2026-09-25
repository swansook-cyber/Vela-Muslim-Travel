import pytest

from app import admin_review_progress


@pytest.mark.asyncio
async def test_review_progress_counts_ready_and_blocked(monkeypatch) -> None:
    rows = [
        {
            "province": "นครศรีธรรมราช",
            "review_state": "DISCOVERED",
            "latitude": None,
            "longitude": None,
            "source_type": "PUBLIC_WEB_SOURCE",
            "source_reference": "https://example.com/a",
            "proposed_trust_status": "UNVERIFIED",
            "certification_expires_at": None,
        },
        {
            "province": "นครศรีธรรมราช",
            "review_state": "GEOCODED",
            "latitude": 8.4,
            "longitude": 99.9,
            "source_type": "PUBLIC_WEB_SOURCE",
            "source_reference": "https://example.com/b",
            "proposed_trust_status": "UNVERIFIED",
            "certification_expires_at": None,
        },
        {
            "province": "นครราชสีมา",
            "review_state": "APPROVED",
            "latitude": 14.6,
            "longitude": 101.4,
            "source_type": "PUBLIC_WEB_SOURCE",
            "source_reference": "https://example.com/c",
            "proposed_trust_status": "UNVERIFIED",
            "certification_expires_at": None,
        },
    ]

    async def fake_list_candidates(session, review_state, limit):
        return rows

    monkeypatch.setattr(
        admin_review_progress,
        "list_candidates",
        fake_list_candidates,
    )

    result = await admin_review_progress.load_candidate_review_progress(None)

    assert result["pending"] == 2
    assert result["ready_to_approve"] == 1
    assert result["blocked"] == 1

    nakhon = next(
        item
        for item in result["provinces"]
        if item["province"] == "นครศรีธรรมราช"
    )
    assert nakhon == {
        "province": "นครศรีธรรมราช",
        "pending": 2,
        "ready_to_approve": 1,
        "blocked": 1,
    }
