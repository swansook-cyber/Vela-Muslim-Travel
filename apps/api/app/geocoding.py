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


async def search_places(query: str, limit: int = 5) -> list[GeocodingResult]:
    normalized = query.strip()
    if len(normalized) < 2:
        return []

    if settings.geocoding_provider.lower() != "nominatim":
        raise GeocodingError(
            f"Unsupported geocoding provider: {settings.geocoding_provider}"
        )

    url = f"{settings.nominatim_base_url.rstrip('/')}/search"
    params = {
        "q": normalized,
        "format": "jsonv2",
        "countrycodes": "th",
        "addressdetails": "1",
        "limit": min(max(limit, 1), 5),
        "accept-language": "th,en",
    }
    headers = {
        "User-Agent": settings.geocoding_user_agent,
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
        response = await client.get(url, params=params)

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
