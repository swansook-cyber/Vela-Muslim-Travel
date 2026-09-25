import pytest
from fastapi import HTTPException

from app import main
from app.google_places import GooglePlaceLocation


@pytest.mark.asyncio
async def test_admin_google_place_resolver_returns_suggestion(monkeypatch) -> None:
    async def fake_get_candidate(session, candidate_id):
        return {
            "id": candidate_id,
            "external_provider": "google_business",
            "external_id": "ChIJexact",
        }

    async def fake_resolve(place_id):
        assert place_id == "ChIJexact"
        return GooglePlaceLocation(
            place_id=place_id,
            latitude=14.123,
            longitude=101.456,
        )

    monkeypatch.setattr(main, "get_candidate", fake_get_candidate)
    monkeypatch.setattr(main, "resolve_google_place_location", fake_resolve)

    result = await main.admin_resolve_candidate_google_place(
        candidate_id="candidate-1",
        session=None,
        _admin=None,
    )

    assert result.candidate_id == "candidate-1"
    assert result.provider == "google_places"
    assert result.external_id == "ChIJexact"
    assert result.latitude == pytest.approx(14.123)
    assert result.longitude == pytest.approx(101.456)


@pytest.mark.asyncio
async def test_admin_google_place_resolver_rejects_non_google_candidate(
    monkeypatch,
) -> None:
    async def fake_get_candidate(session, candidate_id):
        return {
            "id": candidate_id,
            "external_provider": "makan_halal_guide",
            "external_id": "123",
        }

    monkeypatch.setattr(main, "get_candidate", fake_get_candidate)

    with pytest.raises(HTTPException) as exc_info:
        await main.admin_resolve_candidate_google_place(
            candidate_id="candidate-1",
            session=None,
            _admin=None,
        )

    assert exc_info.value.status_code == 409
