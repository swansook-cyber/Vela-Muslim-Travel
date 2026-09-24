from enum import StrEnum

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
    province: str | None = None
    latitude: float
    longitude: float
    distance_m: float | None = None
    route_progress: float | None = None
    trust_status: str | None = None
    verification_source_type: str | None = None
    verified_at: str | None = None


class RouteSummary(BaseModel):
    distance_m: float
    duration_s: float


class AlongRouteResponse(BaseModel):
    route: RouteSummary
    places: list[PlaceResult]
