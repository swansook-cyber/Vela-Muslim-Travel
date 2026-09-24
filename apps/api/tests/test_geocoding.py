import pytest

from app import geocoding


@pytest.fixture(autouse=True)
def clear_geocoding_cache() -> None:
    geocoding._cache.clear()


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


@pytest.mark.asyncio
async def test_geocoding_result_is_cached(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    async def fake_search(
        query: str,
        limit: int,
    ) -> list[geocoding.GeocodingResult]:
        nonlocal calls
        calls += 1
        return [
            geocoding.GeocodingResult(
                display_name=f"{query} result",
                latitude=14.0,
                longitude=101.0,
            )
        ]

    monkeypatch.setattr(geocoding.settings, "geocoding_provider", "nominatim")
    monkeypatch.setattr(geocoding, "_search_nominatim", fake_search)

    first = await geocoding.search_places("เขาใหญ่")
    second = await geocoding.search_places("เขาใหญ่")

    assert calls == 1
    assert first == second


@pytest.mark.asyncio
async def test_geocoding_limit_is_clamped_before_provider_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_limits: list[int] = []

    async def fake_search(
        query: str,
        limit: int,
    ) -> list[geocoding.GeocodingResult]:
        seen_limits.append(limit)
        return []

    monkeypatch.setattr(geocoding.settings, "geocoding_provider", "nominatim")
    monkeypatch.setattr(geocoding, "_search_nominatim", fake_search)

    await geocoding.search_places("เพชรบุรี", limit=50)

    assert seen_limits == [5]
