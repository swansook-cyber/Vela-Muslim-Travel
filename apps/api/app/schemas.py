from datetime import time
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class PlaceType(StrEnum):
    RESTAURANT = "RESTAURANT"
    ACCOMMODATION = "ACCOMMODATION"
    MOSQUE = "MOSQUE"
    PRAYER_ROOM = "PRAYER_ROOM"


class Coordinate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class NearbyRequest(Coordinate):
    radius_m: int = Field(default=5000, ge=100, le=50000)
    place_types: list[PlaceType] | None = None
    limit: int = Field(default=50, ge=1, le=200)


class AlongRouteRequest(BaseModel):
    origin: Coordinate
    destination: Coordinate
    corridor_radius_m: int = Field(default=5000, ge=100, le=50000)
    place_types: list[PlaceType] | None = None
    limit: int = Field(default=100, ge=1, le=300)


class PlaceResult(BaseModel):
    id: str
    slug: str
    place_type: PlaceType
    name_th: str
    name_en: str | None = None
    address: str | None = None
    district: str | None = None
    province: str | None = None
    phone: str | None = None
    website_url: str | None = None
    social_url: str | None = None
    latitude: float
    longitude: float
    distance_m: float | None = None
    route_progress: float | None = None
    trust_status: str | None = None
    verification_source_type: str | None = None
    source_reference: str | None = None
    verified_at: str | None = None
    expires_at: str | None = None
    verification_expired: bool = False
    parking: bool | None = None
    cuisine: list[str] | None = None
    opening_hours: dict | None = None
    takeaway: bool | None = None
    delivery: bool | None = None
    price_level: int | None = None
    halal_food_available: bool | None = None
    prayer_space_available: bool | None = None
    alcohol_policy: str | None = None
    bidet_available: bool | None = None
    family_friendly: bool | None = None
    nearest_mosque_distance_m: int | None = None
    check_in_time: time | None = None
    check_out_time: time | None = None
    friday_prayer: bool | None = None
    women_prayer_area: bool | None = None
    ablution_available: bool | None = None


class GeoJsonLineString(BaseModel):
    type: Literal["LineString"] = "LineString"
    coordinates: list[list[float]]


class RouteSummary(BaseModel):
    distance_m: float
    duration_s: float
    geometry: GeoJsonLineString


class AlongRouteResponse(BaseModel):
    route: RouteSummary
    places: list[PlaceResult]


class GeocodeResult(BaseModel):
    display_name: str
    latitude: float
    longitude: float
    category: str | None = None
    place_type: str | None = None
