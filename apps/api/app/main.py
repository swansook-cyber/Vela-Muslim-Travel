from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .admin_queries import (
    get_candidate,
    list_candidates,
    promote_candidate,
    update_candidate_review,
)
from .admin_schemas import (
    CandidatePromoteRequest,
    CandidatePromoteResponse,
    CandidateResult,
    CandidateReviewState,
    CandidateReviewUpdate,
)
from .config import get_settings
from .db import get_db
from .queries import find_nearby_places, find_place_by_slug, find_places_along_route
from .routing import RoutingError, get_route
from .security import require_admin
from .schemas import (
    AlongRouteRequest,
    AlongRouteResponse,
    GeoJsonLineString,
    NearbyRequest,
    PlaceResult,
    RouteSummary,
)

DbSession = Annotated[AsyncSession, Depends(get_db)]
AdminGuard = Annotated[None, Depends(require_admin)]
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


@app.get("/admin/candidates", response_model=list[CandidateResult])
async def admin_candidates(
    session: DbSession,
    _admin: AdminGuard,
    review_state: CandidateReviewState | None = None,
    limit: int = 100,
) -> list[CandidateResult]:
    rows = await list_candidates(session, review_state=review_state, limit=min(limit, 500))
    return [CandidateResult(**row) for row in rows]


@app.patch("/admin/candidates/{candidate_id}", response_model=CandidateResult)
async def admin_update_candidate(
    candidate_id: str,
    update: CandidateReviewUpdate,
    session: DbSession,
    _admin: AdminGuard,
) -> CandidateResult:
    existing = await get_candidate(session, candidate_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    latitude = update.latitude if update.latitude is not None else existing["latitude"]
    longitude = update.longitude if update.longitude is not None else existing["longitude"]
    review_state = update.review_state or CandidateReviewState(existing["review_state"])
    review_note = (
        update.review_note
        if update.review_note is not None
        else existing["review_note"]
    )

    if (latitude is None) != (longitude is None):
        raise HTTPException(
            status_code=422,
            detail="Latitude and longitude must be set together",
        )

    if review_state == CandidateReviewState.APPROVED and latitude is None:
        raise HTTPException(
            status_code=422,
            detail="Approved candidates require reviewed coordinates",
        )

    row = await update_candidate_review(
        session=session,
        candidate_id=candidate_id,
        latitude=latitude,
        longitude=longitude,
        review_state=review_state,
        review_note=review_note,
    )
    await session.commit()
    return CandidateResult(**row)


@app.post(
    "/admin/candidates/{candidate_id}/promote",
    response_model=CandidatePromoteResponse,
)
async def admin_promote_candidate(
    candidate_id: str,
    request: CandidatePromoteRequest,
    session: DbSession,
    _admin: AdminGuard,
) -> CandidatePromoteResponse:
    candidate = await get_candidate(session, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if candidate["review_state"] != CandidateReviewState.APPROVED.value:
        raise HTTPException(
            status_code=409,
            detail="Candidate must be APPROVED before promotion",
        )

    if candidate["latitude"] is None or candidate["longitude"] is None:
        raise HTTPException(
            status_code=409,
            detail="Candidate requires reviewed coordinates before promotion",
        )

    place_id = await promote_candidate(
        session=session,
        candidate=candidate,
        slug=request.slug,
        name_th=request.name_th or candidate["name"],
    )
    await session.commit()

    return CandidatePromoteResponse(
        candidate_id=candidate_id,
        place_id=place_id,
        slug=request.slug,
    )
