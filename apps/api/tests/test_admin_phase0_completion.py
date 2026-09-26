import pytest

from app import admin_phase0_completion
from app.tools.pilot_readiness import ProvinceReadiness


@pytest.mark.asyncio
async def test_phase0_completion_reports_blockers(monkeypatch) -> None:
    async def fake_list_candidates(
        session,
        review_state,
        province=None,
        place_type=None,
        pilot_only=False,
        limit=100,
    ):
        assert pilot_only is True
        return [
            {"review_state": "DISCOVERED"},
            {"review_state": "GEOCODED"},
            {"review_state": "APPROVED"},
            {"review_state": "PROMOTED"},
            {"review_state": "REJECTED"},
        ]

    async def fake_review_progress(session):
        return {
            "pending": 2,
            "manual_hold": 1,
            "google_fast_lane": 1,
        }

    async def fake_readiness():
        return [
            ProvinceReadiness(
                province="นครศรีธรรมราช",
                restaurants=1,
                mosques=0,
                accommodation=1,
            )
        ]

    monkeypatch.setattr(
        admin_phase0_completion,
        "list_candidates",
        fake_list_candidates,
    )
    monkeypatch.setattr(
        admin_phase0_completion,
        "load_candidate_review_progress",
        fake_review_progress,
    )
    monkeypatch.setattr(
        admin_phase0_completion,
        "load_readiness",
        fake_readiness,
    )

    result = await admin_phase0_completion.load_phase0_completion(None)

    assert result["mechanical_ready"] is False
    assert result["candidate_review_complete"] is False
    assert result["promotion_queue_complete"] is False
    assert result["production_coverage_ready"] is False
    assert result["active_review_pending"] == 2
    assert result["approved_waiting_promotion"] == 1
    assert result["promoted_candidates"] == 1
    assert result["rejected_candidates"] == 1
    assert result["manual_hold"] == 1
    assert result["google_fast_lane"] == 1
    assert len(result["blockers"]) == 3


@pytest.mark.asyncio
async def test_phase0_completion_becomes_mechanically_ready(monkeypatch) -> None:
    async def fake_list_candidates(
        session,
        review_state,
        province=None,
        place_type=None,
        pilot_only=False,
        limit=100,
    ):
        return [
            {"review_state": "PROMOTED"},
            {"review_state": "PROMOTED"},
            {"review_state": "REJECTED"},
        ]

    async def fake_review_progress(session):
        return {
            "pending": 0,
            "manual_hold": 0,
            "google_fast_lane": 0,
        }

    async def fake_readiness():
        return [
            ProvinceReadiness(
                province=f"province-{index}",
                restaurants=1,
                mosques=1,
                accommodation=1 if index < 2 else 0,
            )
            for index in range(7)
        ]

    monkeypatch.setattr(
        admin_phase0_completion,
        "list_candidates",
        fake_list_candidates,
    )
    monkeypatch.setattr(
        admin_phase0_completion,
        "load_candidate_review_progress",
        fake_review_progress,
    )
    monkeypatch.setattr(
        admin_phase0_completion,
        "load_readiness",
        fake_readiness,
    )

    result = await admin_phase0_completion.load_phase0_completion(None)

    assert result["mechanical_ready"] is True
    assert result["candidate_review_complete"] is True
    assert result["promotion_queue_complete"] is True
    assert result["production_coverage_ready"] is True
    assert result["blockers"] == []
    assert result["manual_acceptance_required"] is True
    assert len(result["manual_acceptance_steps"]) == 4
