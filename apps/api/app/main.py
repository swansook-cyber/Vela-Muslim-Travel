from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db
from .queries import find_nearby_places, find_places_along_route
from .routing import RoutingError, get_route
from .schemas import AlongRouteRequest, AlongRouteResponse, NearbyRequest, PlaceResult, RouteSummary

app = FastAPI(
    title="Vela Muslim Travel API",
    version="0.1.0",
    description="Phase 0 API for Muslim travel discovery in Thailand.",
)


@app.get("/health")
async def health(session: AsyncSession = Depends(get_db)) -> dict:
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

    return {"status": "ok"}


@app.post("/places/nearby", response_model=list[PlaceResult])
async def nearby_places(
    request: NearbyRequest,
    session: AsyncSession = Depends(get_db),
) -> list[PlaceResult]:
    rows = await find_nearby_places(session, request)
    return [PlaceResult(**row) for row in rows]


@app.post("/routes/along", response_model=AlongRouteResponse)
async def along_route(
    request: AlongRouteRequest,
    session: AsyncSession = Depends(get_db),
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
        ),
        places=[PlaceResult(**row) for row in rows],
    )
