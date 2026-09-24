from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .db import get_db
from .queries import find_nearby_places, find_place_by_slug, find_places_along_route
from .routing import RoutingError, get_route
from .schemas import (
    AlongRouteRequest,
    AlongRouteResponse,
    GeoJsonLineString,
    NearbyRequest,
    PlaceResult,
    RouteSummary,
)

DbSession = Annotated[AsyncSession, Depends(get_db)]
settings = get_settings()

app = FastAPI(
    title="Vela Muslim Travel API",
    version="0.2.0",
    description="Route-first Muslim travel discovery API for Thailand.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
async def health(session: DbSession) -> dict:
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

    return {"status": "ok", "version": app.version}


@app.get("/places/{slug}", response_model=PlaceResult)
async def place_detail(
    slug: str,
    session: DbSession,
) -> PlaceResult:
    row = await find_place_by_slug(session, slug)
    if row is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return PlaceResult(**row)


@app.post("/places/nearby", response_model=list[PlaceResult])
async def nearby_places(
    request: NearbyRequest,
    session: DbSession,
) -> list[PlaceResult]:
    rows = await find_nearby_places(session, request)
    return [PlaceResult(**row) for row in rows]


@app.post("/routes/along", response_model=AlongRouteResponse)
async def along_route(
    request: AlongRouteRequest,
    session: DbSession,
) -> AlongRouteResponse:
    try:
        route = await get_route(request.origin, request.destination)
    except RoutingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    rows = await find_places_along_route(
        session=session,
        route=route,
        corridor_radius_m=request.corridor_radius_m,
        place_types=request.place_types,
        limit=request.limit,
    )

    return AlongRouteResponse(
        route=RouteSummary(
            distance_m=route.distance_m,
            duration_s=route.duration_s,
            geometry=GeoJsonLineString(coordinates=route.coordinates),
        ),
        places=[PlaceResult(**row) for row in rows],
    )
