import pytest

from app import google_places


@pytest.fixture(autouse=True)
def clear_google_places_cache() -> None:
    google_places._cache.clear()


@pytest.mark.asyncio
async def test_google_places_requires_configuration(monkeypatch) -> None:
    monkeypatch.setattr(google_places.settings, "google_places_api_key", None)

    with pytest.raises(
        google_places.GooglePlacesNotConfigured,
        match="not configured",
    ):
        await google_places.resolve_google_place_location("ChIJtest")


@pytest.mark.asyncio
async def test_google_places_resolves_id_and_location(monkeypatch) -> None:
    seen: dict[str, object] = {}

    class FakeResponse:
        status_code = 200

        @staticmethod
        def json() -> dict:
            return {
                "id": "ChIJtest",
                "location": {
                    "latitude": 14.1234567,
                    "longitude": 101.7654321,
                },
                "formattedAddress": "165 Moo 15 Thanarat Rd, Mu Si, Pak Chong",
            }

    class FakeClient:
        def __init__(self, *args, **kwargs):
            seen["headers"] = kwargs.get("headers")
            seen["timeout"] = kwargs.get("timeout")

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url: str):
            seen["url"] = url
            return FakeResponse()

    monkeypatch.setattr(
        google_places.settings,
        "google_places_api_key",
        "test-key",
    )
    monkeypatch.setattr(google_places.httpx, "AsyncClient", FakeClient)

    result = await google_places.resolve_google_place_location("ChIJtest")

    assert result.place_id == "ChIJtest"
    assert result.latitude == pytest.approx(14.1234567)
    assert result.longitude == pytest.approx(101.7654321)
    assert result.formatted_address == "165 Moo 15 Thanarat Rd, Mu Si, Pak Chong"
    assert str(seen["url"]).endswith("/v1/places/ChIJtest")
    assert seen["headers"] == {
        "Accept": "application/json",
        "X-Goog-Api-Key": "test-key",
        "X-Goog-FieldMask": "id,location,formattedAddress",
    }


@pytest.mark.asyncio
async def test_google_places_rejects_mismatched_id(monkeypatch) -> None:
    class FakeResponse:
        status_code = 200

        @staticmethod
        def json() -> dict:
            return {
                "id": "ChIJdifferent",
                "location": {
                    "latitude": 14.1,
                    "longitude": 101.1,
                },
            }

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url: str):
            return FakeResponse()

    monkeypatch.setattr(
        google_places.settings,
        "google_places_api_key",
        "test-key",
    )
    monkeypatch.setattr(google_places.httpx, "AsyncClient", FakeClient)

    with pytest.raises(
        google_places.GooglePlacesError,
        match="different place ID",
    ):
        await google_places.resolve_google_place_location("ChIJtest")


@pytest.mark.asyncio
async def test_google_places_reuses_cached_location(monkeypatch) -> None:
    calls = 0

    class FakeResponse:
        status_code = 200

        @staticmethod
        def json() -> dict:
            return {
                "id": "ChIJcached",
                "location": {
                    "latitude": 14.2,
                    "longitude": 101.2,
                },
            }

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url: str):
            nonlocal calls
            calls += 1
            return FakeResponse()

    monkeypatch.setattr(
        google_places.settings,
        "google_places_api_key",
        "test-key",
    )
    monkeypatch.setattr(google_places.httpx, "AsyncClient", FakeClient)

    first = await google_places.resolve_google_place_location("ChIJcached")
    second = await google_places.resolve_google_place_location("ChIJcached")

    assert calls == 1
    assert first == second
