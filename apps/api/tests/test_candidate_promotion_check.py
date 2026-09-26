import pytest

from app import main
from app.admin_schemas import CandidatePromoteRequest


@pytest.mark.asyncio
async def test_promotion_preflight_returns_duplicate_and_slug_status(monkeypatch) -> None:
    async def fake_get_candidate(session, candidate_id):
        return {
            "id": candidate_id,
            "review_state": "APPROVED",
            "latitude": 14.7,
            "longitude": 101.4,
            "place_type": "RESTAURANT",
        }

    async def fake_check(session, candidate, slug):
        assert candidate["id"] == "candidate-1"
        assert slug == "candidate-slug"
        return {
            "can_promote": False,
            "slug_exists": False,
            "duplicate": {
                "id": "place-1",
                "slug": "existing-place",
                "name_th": "ร้านเดิม",
                "distance_m": 42.5,
            },
        }

    monkeypatch.setattr(main, "get_candidate", fake_get_candidate)
    monkeypatch.setattr(main, "check_candidate_promotion", fake_check)

    result = await main.admin_candidate_promotion_check(
        candidate_id="candidate-1",
        request=CandidatePromoteRequest(slug="candidate-slug"),
        session=None,
        _admin=None,
    )

    assert result.can_promote is False
    assert result.slug_exists is False
    assert result.duplicate is not None
    assert result.duplicate.slug == "existing-place"
    assert result.duplicate.distance_m == pytest.approx(42.5)


@pytest.mark.asyncio
async def test_promotion_preflight_requires_approved_candidate(monkeypatch) -> None:
    async def fake_get_candidate(session, candidate_id):
        return {
            "id": candidate_id,
            "review_state": "GEOCODED",
            "latitude": 14.7,
            "longitude": 101.4,
            "place_type": "RESTAURANT",
        }

    monkeypatch.setattr(main, "get_candidate", fake_get_candidate)

    with pytest.raises(main.HTTPException) as exc_info:
        await main.admin_candidate_promotion_check(
            candidate_id="candidate-1",
            request=CandidatePromoteRequest(slug="candidate-slug"),
            session=None,
            _admin=None,
        )

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_promotion_preflight_blocks_expired_certification(monkeypatch) -> None:
    from datetime import UTC, datetime, timedelta

    async def fake_get_candidate(session, candidate_id):
        return {
            "id": candidate_id,
            "review_state": "APPROVED",
            "latitude": 14.7,
            "longitude": 101.4,
            "place_type": "RESTAURANT",
            "proposed_trust_status": "HALAL_CERTIFIED",
            "certification_expires_at": datetime.now(UTC) - timedelta(days=1),
        }

    async def fake_check(session, candidate, slug):
        return {
            "can_promote": True,
            "slug_exists": False,
            "duplicate": None,
        }

    monkeypatch.setattr(main, "get_candidate", fake_get_candidate)
    monkeypatch.setattr(main, "check_candidate_promotion", fake_check)

    result = await main.admin_candidate_promotion_check(
        candidate_id="candidate-expired",
        request=CandidatePromoteRequest(slug="candidate-expired"),
        session=None,
        _admin=None,
    )

    assert result.can_promote is False
    assert result.slug_exists is False
    assert result.duplicate is None
    assert result.promotion_blockers == [
        "certified candidate requires current non-expired certificate"
    ]
