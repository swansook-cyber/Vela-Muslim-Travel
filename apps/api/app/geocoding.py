import asyncio
import time
from dataclasses import dataclass

import httpx

from .config import get_settings

settings = get_settings()


@dataclass(slots=True)
class GeocodingResult:
    display_name: str
    latitude: float
    longitude: float
    category: str | None = None
    place_type: str | None = None


class GeocodingError(RuntimeError):
    pass


_cache: dict[str, tuple[float, list[GeocodingResult]]] = {}
_provider_lock = asyncio.Lock()
_last_provider_request_at = 0.0


def _cache_key(query: str, limit: int) -> str:
    return f"{query.casefold()}|{limit}"


def _get_cached(key: str) -> list[GeocodingResult] | None:
    cached = _cache.get(key)
    if cached is None:
        return None

    expires_at, results = cached
    if expires_at <= time.monotonic():
        _cache.pop(key, None)
        return None

    return list(results)


def _set_cached(key: str, results: list[GeocodingResult]) -> None:
    if len(_cache) >= settings.geocoding_cache_max_entries:
        oldest_key = min(_cache, key=lambda item: _cache[item][0])
        _cache.pop(oldest_key, None)

    _cache[key] = (
        time.monotonic() + settings.geocoding_cache_ttl_seconds,
        list(results),
    )


async def _search_nominatim(
    query: str,
    limit: int,
) -> list[GeocodingResult]:
    global _last_provider_request_at

    url = f"{settings.nominatim_base_url.rstrip('/')}/search"
    params = {
        "q": query,
        "format": "jsonv2",
        "countrycodes": "th",
        "addressdetails": "1",
        "limit": limit,
        "accept-language": "th,en",
    }
    headers = {
        "User-Agent": settings.geocoding_user_agent,
        "Accept": "application/json",
    }

    async with _provider_lock:
        elapsed = time.monotonic() - _last_provider_request_at
        delay = settings.geocoding_min_interval_seconds - elapsed
        if delay > 0:
            await asyncio.sleep(delay)

        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            response = await client.get(url, params=params)

        _last_provider_request_at = time.monotonic()

    if response.status_code != 200:
        raise GeocodingError(
            f"Geocoding provider returned HTTP {response.status_code}"
        )

    results: list[GeocodingResult] = []
    for item in response.json():
        try:
            latitude = float(item["lat"])
            longitude = float(item["lon"])
            display_name = str(item["display_name"])
        except (KeyError, TypeError, ValueError) as exc:
            raise GeocodingError("Geocoding provider returned invalid data") from exc

        results.append(
            GeocodingResult(
                display_name=display_name,
                latitude=latitude,
                longitude=longitude,
                category=item.get("category"),
                place_type=item.get("type"),
            )
        )

    return results


async def search_places(query: str, limit: int = 5) -> list[GeocodingResult]:
    normalized = query.strip()
    if len(normalized) < 2:
        return []

    safe_limit = min(max(limit, 1), 5)
    key = _cache_key(normalized, safe_limit)
    cached = _get_cached(key)
    if cached is not None:
        return cached

    if settings.geocoding_provider.lower() != "nominatim":
        raise GeocodingError(
            f"Unsupported geocoding provider: {settings.geocoding_provider}"
        )

    results = await _search_nominatim(normalized, safe_limit)
    _set_cached(key, results)
    return results
