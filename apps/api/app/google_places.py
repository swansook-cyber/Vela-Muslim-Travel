from __future__ import annotations

from dataclasses import dataclass
import time
from urllib.parse import quote

import httpx

from .config import get_settings

settings = get_settings()


@dataclass(slots=True)
class GooglePlaceLocation:
    place_id: str
    latitude: float
    longitude: float


class GooglePlacesError(RuntimeError):
    pass


class GooglePlacesNotConfigured(GooglePlacesError):
    pass


_cache: dict[str, tuple[float, GooglePlaceLocation]] = {}


def _get_cached(place_id: str) -> GooglePlaceLocation | None:
    cached = _cache.get(place_id)
    if cached is None:
        return None

    expires_at, result = cached
    if expires_at <= time.monotonic():
        _cache.pop(place_id, None)
        return None

    return result


def _set_cached(place_id: str, result: GooglePlaceLocation) -> None:
    if len(_cache) >= settings.google_places_cache_max_entries:
        oldest_key = min(_cache, key=lambda key: _cache[key][0])
        _cache.pop(oldest_key, None)

    _cache[place_id] = (
        time.monotonic() + settings.google_places_cache_ttl_seconds,
        result,
    )


async def resolve_google_place_location(place_id: str) -> GooglePlaceLocation:
    normalized = place_id.strip()
    if not normalized:
        raise GooglePlacesError("Google place ID is required")

    if not settings.google_places_api_key:
        raise GooglePlacesNotConfigured("Google Places API is not configured")

    cached = _get_cached(normalized)
    if cached is not None:
        return cached

    url = (
        f"{settings.google_places_base_url.rstrip('/')}/v1/places/"
        f"{quote(normalized, safe='')}"
    )
    headers = {
        "Accept": "application/json",
        "X-Goog-Api-Key": settings.google_places_api_key,
        "X-Goog-FieldMask": "id,location",
    }

    async with httpx.AsyncClient(
        timeout=settings.google_places_timeout_seconds,
        headers=headers,
    ) as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise GooglePlacesError(
            f"Google Places provider returned HTTP {response.status_code}"
        )

    try:
        payload = response.json()
        returned_id = str(payload["id"])
        location = payload["location"]
        latitude = float(location["latitude"])
        longitude = float(location["longitude"])
    except (KeyError, TypeError, ValueError) as exc:
        raise GooglePlacesError("Google Places provider returned invalid data") from exc

    if returned_id != normalized:
        raise GooglePlacesError("Google Places provider returned a different place ID")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise GooglePlacesError("Google Places provider returned invalid coordinates")

    result = GooglePlaceLocation(
        place_id=returned_id,
        latitude=latitude,
        longitude=longitude,
    )
    _set_cached(normalized, result)
    return result
