from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .admin_candidate_readiness import (
    candidate_readiness_passes,
    load_candidate_readiness,
)
from .admin_phase0_completion import load_phase0_completion
from .admin_places import get_admin_place, list_admin_places, update_admin_place
from .admin_queries import (
    check_candidate_promotion,
    get_admin_dashboard,
    get_candidate,
    list_admin_audit,
    list_candidates,
    log_admin_action,
    promote_candidate,
    update_candidate_review,
)
from .admin_review_progress import load_candidate_review_progress
from .admin_schemas import (
    AdminAuditEntry,
    AdminDashboard,
    AdminPlaceResult,
    AdminPlaceUpdate,
    AdminVerificationCreate,
    AdminVerificationResult,
    CandidateCoordinateBatchItem,
    CandidateCoordinateBatchRequest,
    CandidateCoordinateBatchResponse,
    CandidateCoordinateSuggestion,
    CandidatePromoteRequest,
    CandidatePromoteResponse,
    CandidatePromotionCheckResponse,
    CandidateProvinceReadiness,
    CandidateReadinessResponse,
    CandidateResult,
    CandidateReviewProgressResponse,
    CandidateReviewState,
    CandidateReviewTask,
    CandidateReviewUpdate,
    Phase0AcceptanceRequest,
    Phase0CompletionResponse,
    PilotProvinceReadiness,
    PilotReadinessResponse,
)
from .admin_verifications import (
    add_place_verification,
    list_place_verifications,
    validate_verification_claim,
)
from .candidate_review import (
    candidate_approval_blockers,
    candidate_maps_search_url,
    candidate_promotion_blockers,
    candidate_review_transition_allowed,
    candidate_review_warnings,
)
from .config import get_settings
from .db import get_db
from .geocoding import GeocodingError, search_places
from .google_places import (
    GooglePlacesError,
    GooglePlacesNotConfigured,
    resolve_google_place_location,
)
from .queries import find_nearby_places, find_place_by_slug, find_places_along_route
from .routing import RoutingError, get_route, get_route_via
from .schemas import (
    AlongRouteRequest,
    AlongRouteResponse,
    DetourRequest,
    DetourResponse,
    GeocodeResult,
    GeoJsonLineString,
    NearbyRequest,
    PlaceResult,
    PlaceType,
    RouteSummary,
)
from .security import require_admin
from .tools.pilot_readiness import load_readiness, readiness_passes

DbSession = Annotated[AsyncSession, Depends(get_db)]
AdminGuard = Annotated[None, Depends(require_admin)]
settings = get_settings()

app = FastAPI(
    title="Vela Muslim Travel API",
    version="0.2.0",
    description="Route-first Muslim travel discovery API for Thailand.",
)

@app.middleware("http")
async def admin_no_store_middleware(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/admin"):
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["Pragma"] = "no-cache"
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["*"],
)


@app.get("/health")
async def health(session: DbSession) -> dict:
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

    return {"status": "ok", "version": app.version}


@app.get("/geocode/search", response_model=list[GeocodeResult])
async def geocode_search(q: str) -> list[GeocodeResult]:
    if len(q.strip()) < 2:
        return []

    try:
        results = await search_places(q)
    except GeocodingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return [
        GeocodeResult(
            display_name=item.display_name,
            latitude=item.latitude,
            longitude=item.longitude,
            category=item.category,
            place_type=item.place_type,
        )
        for item in results
    ]


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


@app.post("/routes/detour", response_model=DetourResponse)
async def route_detour(request: DetourRequest) -> DetourResponse:
    try:
        route = await get_route_via(
            request.origin,
            request.stop,
            request.destination,
        )
    except RoutingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return DetourResponse(
        route_distance_m=route.distance_m,
        route_duration_s=route.duration_s,
        added_distance_m=max(0.0, route.distance_m - request.base_distance_m),
        added_duration_s=max(0.0, route.duration_s - request.base_duration_s),
    )


@app.get("/admin/candidate-readiness", response_model=CandidateReadinessResponse)
async def admin_candidate_readiness(
    session: DbSession,
    _admin: AdminGuard,
) -> CandidateReadinessResponse:
    rows = await load_candidate_readiness(session)
    provinces = [CandidateProvinceReadiness(**row) for row in rows]
    return CandidateReadinessResponse(
        ready=candidate_readiness_passes(rows),
        provinces=provinces,
    )


@app.get(
    "/admin/candidate-review-progress",
    response_model=CandidateReviewProgressResponse,
)
async def admin_candidate_review_progress(
    session: DbSession,
    _admin: AdminGuard,
) -> CandidateReviewProgressResponse:
    progress = await load_candidate_review_progress(session)
    return CandidateReviewProgressResponse(**progress)






@app.post("/admin/phase0-acceptance", response_model=Phase0CompletionResponse)
async def admin_phase0_acceptance(
    request: Phase0AcceptanceRequest,
    session: DbSession,
    _admin: AdminGuard,
) -> Phase0CompletionResponse:
    summary = await load_phase0_completion(session)
    if not summary["mechanical_ready"]:
        raise HTTPException(
            status_code=409,
            detail="Phase 0 must be mechanically ready before final acceptance",
        )

    checks = {
        "route_smoke_2km_checked": request.route_smoke_2km_checked,
        "route_smoke_5km_core_pass": request.route_smoke_5km_core_pass,
        "route_smoke_10km_checked": request.route_smoke_10km_checked,
        "detours_and_evidence_checked": request.detours_and_evidence_checked,
    }
    missing = [name for name, passed in checks.items() if not passed]
    if missing:
        raise HTTPException(
            status_code=422,
            detail="Final acceptance checks incomplete: " + ", ".join(missing),
        )

    await log_admin_action(
        session,
        action="PHASE0_ACCEPTANCE",
        entity_type="phase0",
        entity_id="pilot",
        details={
            **checks,
            "note": request.note,
        },
    )
    await session.commit()

    refreshed = await load_phase0_completion(session)
    return Phase0CompletionResponse(**refreshed)


@app.get("/admin/phase0-completion", response_model=Phase0CompletionResponse)
async def admin_phase0_completion(
    session: DbSession,
    _admin: AdminGuard,
) -> Phase0CompletionResponse:
    summary = await load_phase0_completion(session)
    return Phase0CompletionResponse(**summary)


@app.get("/admin/pilot-readiness", response_model=PilotReadinessResponse)
async def admin_pilot_readiness(
    _admin: AdminGuard,
) -> PilotReadinessResponse:
    items = await load_readiness()
    provinces = [
        PilotProvinceReadiness(
            province=item.province,
            restaurants=item.restaurants,
            mosques=item.mosques,
            accommodation=item.accommodation,
            total=item.total,
            missing_types=item.missing_types,
        )
        for item in items
    ]
    return PilotReadinessResponse(
        ready=readiness_passes(items),
        accommodation_provinces=sum(
            1 for item in items if item.accommodation > 0
        ),
        provinces=provinces,
    )


@app.get("/admin/dashboard", response_model=AdminDashboard)
async def admin_dashboard(
    session: DbSession,
    _admin: AdminGuard,
) -> AdminDashboard:
    row = await get_admin_dashboard(session)
    return AdminDashboard(
        **row,
        google_places_resolver_enabled=bool(settings.google_places_api_key),
    )


@app.get("/admin/audit", response_model=list[AdminAuditEntry])
async def admin_audit(
    session: DbSession,
    _admin: AdminGuard,
    limit: int = 50,
) -> list[AdminAuditEntry]:
    rows = await list_admin_audit(session, limit=min(max(limit, 1), 200))
    return [AdminAuditEntry(**row) for row in rows]


@app.get("/admin/places", response_model=list[AdminPlaceResult])
async def admin_places(
    session: DbSession,
    _admin: AdminGuard,
    include_inactive: bool = True,
    limit: int = 200,
) -> list[AdminPlaceResult]:
    rows = await list_admin_places(
        session,
        include_inactive=include_inactive,
        limit=min(max(limit, 1), 500),
    )
    return [AdminPlaceResult(**row) for row in rows]


@app.patch("/admin/places/{place_id}", response_model=AdminPlaceResult)
async def admin_update_place(
    place_id: str,
    update: AdminPlaceUpdate,
    session: DbSession,
    _admin: AdminGuard,
) -> AdminPlaceResult:
    existing = await get_admin_place(session, place_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Place not found")

    changes = update.model_dump(exclude_unset=True)

    if ("latitude" in changes) != ("longitude" in changes):
        raise HTTPException(
            status_code=422,
            detail="Latitude and longitude must be updated together",
        )

    try:
        row = await update_admin_place(session, place_id, changes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if row is None:
        raise HTTPException(status_code=404, detail="Place not found")

    await log_admin_action(
        session,
        action="UPDATE_PLACE",
        entity_type="place",
        entity_id=place_id,
        details={
            "changed_fields": sorted(changes.keys()),
            "active": row["active"],
            "slug": row["slug"],
        },
    )
    await session.commit()
    return AdminPlaceResult(**row)


@app.get(
    "/admin/places/{place_id}/verifications",
    response_model=list[AdminVerificationResult],
)
async def admin_place_verifications(
    place_id: str,
    session: DbSession,
    _admin: AdminGuard,
) -> list[AdminVerificationResult]:
    place = await get_admin_place(session, place_id)
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found")

    rows = await list_place_verifications(session, place_id)
    return [AdminVerificationResult(**row) for row in rows]


@app.post(
    "/admin/places/{place_id}/verifications",
    response_model=AdminVerificationResult,
)
async def admin_add_place_verification(
    place_id: str,
    payload: AdminVerificationCreate,
    session: DbSession,
    _admin: AdminGuard,
) -> AdminVerificationResult:
    place = await get_admin_place(session, place_id)
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found")

    try:
        validate_verification_claim(
            place_type=place["place_type"],
            trust_status=payload.trust_status,
            source_type=payload.source_type,
            source_reference=payload.source_reference,
            expires_at=payload.expires_at,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    verification_id = await add_place_verification(
        session,
        place_id=place_id,
        trust_status=payload.trust_status,
        source_type=payload.source_type,
        source_reference=payload.source_reference,
        verified_at=payload.verified_at,
        expires_at=payload.expires_at,
        note=payload.note,
    )
    await log_admin_action(
        session,
        action="ADD_VERIFICATION",
        entity_type="place",
        entity_id=place_id,
        details={
            "verification_id": verification_id,
            "trust_status": payload.trust_status,
            "source_type": payload.source_type,
        },
    )
    await session.commit()

    rows = await list_place_verifications(session, place_id)
    row = next(item for item in rows if item["id"] == verification_id)
    return AdminVerificationResult(**row)


@app.get(
    "/admin/candidates/review-queue",
    response_model=list[CandidateReviewTask],
)
async def admin_candidate_review_queue(
    session: DbSession,
    _admin: AdminGuard,
    review_state: CandidateReviewState = CandidateReviewState.DISCOVERED,
    province: str | None = None,
    place_type: PlaceType | None = None,
    pilot_only: bool = False,
    limit: int = 100,
) -> list[CandidateReviewTask]:
    if review_state not in {
        CandidateReviewState.DISCOVERED,
        CandidateReviewState.GEOCODED,
    }:
        raise HTTPException(
            status_code=422,
            detail="Review queue only supports DISCOVERED or GEOCODED candidates",
        )

    rows = await list_candidates(
        session,
        review_state=review_state,
        province=province,
        place_type=place_type.value if place_type else None,
        pilot_only=pilot_only,
        limit=min(max(limit, 1), 500),
    )

    tasks: list[CandidateReviewTask] = []
    for row in rows:
        blockers = candidate_approval_blockers(row)
        warnings = candidate_review_warnings(row)
        tasks.append(
            CandidateReviewTask(
                **row,
                maps_search_url=candidate_maps_search_url(row),
                approval_blockers=blockers,
                review_warnings=warnings,
                ready_to_approve=(
                    row["review_state"] == CandidateReviewState.GEOCODED.value
                    and not blockers
                ),
            )
        )
    return tasks


@app.post(
    "/admin/candidates/{candidate_id}/resolve-google-place",
    response_model=CandidateCoordinateSuggestion,
)
async def admin_resolve_candidate_google_place(
    candidate_id: str,
    session: DbSession,
    _admin: AdminGuard,
) -> CandidateCoordinateSuggestion:
    candidate = await get_candidate(session, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if candidate.get("external_provider") not in {"google_business", "google_places"}:
        raise HTTPException(
            status_code=409,
            detail="Candidate does not use a Google place provider",
        )

    external_id = candidate.get("external_id")
    if not external_id:
        raise HTTPException(status_code=409, detail="Candidate has no Google place ID")

    try:
        result = await resolve_google_place_location(str(external_id))
    except GooglePlacesNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GooglePlacesError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return CandidateCoordinateSuggestion(
        candidate_id=candidate_id,
        provider="google_places",
        external_id=result.place_id,
        latitude=result.latitude,
        longitude=result.longitude,
        formatted_address=getattr(result, "formatted_address", None),
    )


@app.post(
    "/admin/candidates/resolve-google-places",
    response_model=CandidateCoordinateBatchResponse,
)
async def admin_resolve_candidate_google_places(
    request: CandidateCoordinateBatchRequest,
    session: DbSession,
    _admin: AdminGuard,
) -> CandidateCoordinateBatchResponse:
    if not settings.google_places_api_key:
        raise HTTPException(
            status_code=503,
            detail="Google Places API is not configured",
        )

    results: list[CandidateCoordinateBatchItem] = []
    for candidate_id in request.candidate_ids:
        candidate = await get_candidate(session, candidate_id)
        if candidate is None:
            results.append(
                CandidateCoordinateBatchItem(
                    candidate_id=candidate_id,
                    error="Candidate not found",
                )
            )
            continue

        if candidate.get("external_provider") not in {
            "google_business",
            "google_places",
        }:
            results.append(
                CandidateCoordinateBatchItem(
                    candidate_id=candidate_id,
                    error="Candidate does not use a Google place provider",
                )
            )
            continue

        external_id = candidate.get("external_id")
        if not external_id:
            results.append(
                CandidateCoordinateBatchItem(
                    candidate_id=candidate_id,
                    error="Candidate has no Google place ID",
                )
            )
            continue

        try:
            result = await resolve_google_place_location(str(external_id))
        except GooglePlacesNotConfigured as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except GooglePlacesError as exc:
            results.append(
                CandidateCoordinateBatchItem(
                    candidate_id=candidate_id,
                    error=str(exc),
                )
            )
            continue

        results.append(
            CandidateCoordinateBatchItem(
                candidate_id=candidate_id,
                suggestion=CandidateCoordinateSuggestion(
                    candidate_id=candidate_id,
                    provider="google_places",
                    external_id=result.place_id,
                    latitude=result.latitude,
                    longitude=result.longitude,
                    formatted_address=getattr(result, "formatted_address", None),
                ),
            )
        )

    return CandidateCoordinateBatchResponse(results=results)


@app.get("/admin/candidates", response_model=list[CandidateResult])
async def admin_candidates(
    session: DbSession,
    _admin: AdminGuard,
    review_state: CandidateReviewState | None = None,
    province: str | None = None,
    place_type: PlaceType | None = None,
    limit: int = 100,
) -> list[CandidateResult]:
    rows = await list_candidates(
        session,
        review_state=review_state,
        province=province,
        place_type=place_type.value if place_type else None,
        limit=min(limit, 500),
    )
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
    if not candidate_review_transition_allowed(
        existing["review_state"],
        review_state.value,
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Invalid candidate review transition: "
                f"{existing['review_state']} -> {review_state.value}"
            ),
        )
    review_note = (
        update.review_note
        if update.review_note is not None
        else existing["review_note"]
    )
    review_hold_reason = (
        (update.review_hold_reason.strip() or None)
        if update.review_hold_reason is not None
        else existing["review_hold_reason"]
    )
    source_checked_at = (
        update.source_checked_at
        if update.source_checked_at is not None
        else existing["source_checked_at"]
    )
    coordinates_changed = (
        latitude != existing["latitude"] or longitude != existing["longitude"]
    )
    coordinate_checked_at = (
        update.coordinate_checked_at
        if update.coordinate_checked_at is not None
        else (
            None
            if coordinates_changed
            else existing["coordinate_checked_at"]
        )
    )

    if (latitude is None) != (longitude is None):
        raise HTTPException(
            status_code=422,
            detail="Latitude and longitude must be set together",
        )

    if review_state in {
        CandidateReviewState.GEOCODED,
        CandidateReviewState.APPROVED,
    } and coordinate_checked_at is None:
        raise HTTPException(
            status_code=422,
            detail="Coordinate verification is required before GEOCODED/APPROVED",
        )

    if review_state == CandidateReviewState.APPROVED:
        approval_candidate = {
            **existing,
            "latitude": latitude,
            "longitude": longitude,
            "review_hold_reason": review_hold_reason,
            "source_checked_at": source_checked_at,
            "coordinate_checked_at": coordinate_checked_at,
        }
        blockers = candidate_approval_blockers(
            approval_candidate,
            latitude=latitude,
            longitude=longitude,
        )
        if blockers:
            raise HTTPException(
                status_code=422,
                detail="Cannot approve candidate: " + "; ".join(blockers),
            )

    row = await update_candidate_review(
        session=session,
        candidate_id=candidate_id,
        latitude=latitude,
        longitude=longitude,
        review_state=review_state,
        review_note=review_note,
        review_hold_reason=review_hold_reason,
        source_checked_at=source_checked_at,
        coordinate_checked_at=coordinate_checked_at,
    )
    await log_admin_action(
        session,
        action="REVIEW_CANDIDATE",
        entity_type="place_candidate",
        entity_id=candidate_id,
        details={
            "review_state": review_state.value,
            "latitude": latitude,
            "longitude": longitude,
            "review_hold_reason": review_hold_reason,
            "source_checked_at": (
                source_checked_at.isoformat() if source_checked_at else None
            ),
            "coordinate_checked_at": (
                coordinate_checked_at.isoformat()
                if coordinate_checked_at
                else None
            ),
        },
    )
    await session.commit()
    return CandidateResult(**row)


@app.post(
    "/admin/candidates/{candidate_id}/promotion-check",
    response_model=CandidatePromotionCheckResponse,
)
async def admin_candidate_promotion_check(
    candidate_id: str,
    request: CandidatePromoteRequest,
    session: DbSession,
    _admin: AdminGuard,
) -> CandidatePromotionCheckResponse:
    candidate = await get_candidate(session, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate["review_state"] != CandidateReviewState.APPROVED.value:
        raise HTTPException(
            status_code=409,
            detail="Candidate must be APPROVED before promotion preflight",
        )
    if candidate["latitude"] is None or candidate["longitude"] is None:
        raise HTTPException(
            status_code=409,
            detail="Candidate requires reviewed coordinates before promotion preflight",
        )

    result = await check_candidate_promotion(session, candidate, request.slug)
    promotion_blockers = candidate_promotion_blockers(candidate)
    result["promotion_blockers"] = promotion_blockers
    result["can_promote"] = result["can_promote"] and not promotion_blockers
    return CandidatePromotionCheckResponse(**result)


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

    promotion_blockers = candidate_promotion_blockers(candidate)
    if promotion_blockers:
        raise HTTPException(
            status_code=409,
            detail=promotion_blockers[0],
        )

    try:
        place_id = await promote_candidate(
            session=session,
            candidate=candidate,
            slug=request.slug,
            name_th=request.name_th or candidate["name"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    await log_admin_action(
        session,
        action="PROMOTE_CANDIDATE",
        entity_type="place_candidate",
        entity_id=candidate_id,
        details={
            "place_id": place_id,
            "slug": request.slug,
            "trust_status": candidate["proposed_trust_status"],
        },
    )
    await session.commit()

    return CandidatePromoteResponse(
        candidate_id=candidate_id,
        place_id=place_id,
        slug=request.slug,
    )
