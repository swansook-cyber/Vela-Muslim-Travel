import pytest

from app import geocoding


@pytest.mark.asyncio
async def test_short_geocoding_query_does_not_call_provider() -> None:
    assert await geocoding.search_places(" ") == []


@pytest.mark.asyncio
async def test_unknown_geocoding_provider_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(geocoding.settings, "geocoding_provider", "unsupported")

    with pytest.raises(geocoding.GeocodingError, match="Unsupported"):
        await geocoding.search_places("เขาใหญ่")
