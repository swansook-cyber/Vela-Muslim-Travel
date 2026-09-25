from __future__ import annotations

from dataclasses import dataclass
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


async def resolve_google_place_location(place_id: str) -> GooglePlaceLocation:
    normalized = place_id.strip()
    if not normalized:
        raise GooglePlacesError("Google place ID is required")

    if not settings.google_places_api_key:
        raise GooglePlacesNotConfigured("Google Places API is not configured")

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

    return GooglePlaceLocation(
        place_id=returned_id,
        latitude=latitude,
        longitude=longitude,
    )
