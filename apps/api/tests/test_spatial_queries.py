import os
from datetime import datetime

import pytest
from sqlalchemy import text

from app.admin_queries import (
    get_candidate,
    list_candidates,
    promote_candidate,
    update_candidate_review,
)
from app.admin_schemas import CandidateReviewState
from app.db import SessionLocal
from app.queries import find_nearby_places, find_place_by_slug, find_places_along_route
from app.routing import RouteResult
from app.schemas import NearbyRequest, PlaceType
from app.tools.import_candidates import Candidate, apply_candidates
from app.tools.import_reviewed_places import ReviewedPlace, apply_places

pytestmark = pytest.mark.integration

if os.getenv("RUN_INTEGRATION") != "1":
    pytest.skip("PostGIS integration tests are disabled", allow_module_level=True)


@pytest.mark.asyncio
async def test_place_detail_returns_latest_verification() -> None:
    async with SessionLocal() as session:
        row = await find_place_by_slug(session, "test-route-mosque-middle")

    assert row is not None
    assert row["place_type"] == "MOSQUE"
    assert row["trust_status"] == "UNVERIFIED"
    assert row["source_reference"] == "synthetic://phase0-test-fixture"
    assert row["ablution_available"] is True
    assert row["friday_prayer"] is True
    assert row["parking"] is True


@pytest.mark.asyncio
async def test_accommodation_detail_fields_are_returned() -> None:
    async with SessionLocal() as session:
        row = await find_place_by_slug(session, "test-route-accommodation-north")

    assert row is not None
    assert row["halal_food_available"] is True
    assert row["prayer_space_available"] is True
    assert row["bidet_available"] is True
    assert row["nearest_mosque_distance_m"] == 900


@pytest.mark.asyncio
async def test_nearby_returns_only_places_inside_radius() -> None:
    request = NearbyRequest(
        latitude=12.6,
        longitude=100.2,
        radius_m=30_000,
        limit=20,
    )

    async with SessionLocal() as session:
        rows = await find_nearby_places(session, request)

    slugs = {row["slug"] for row in rows}
    assert "test-route-mosque-middle" in slugs
    assert "test-route-far-away" not in slugs


@pytest.mark.asyncio
async def test_nearby_respects_place_type_filter() -> None:
    request = NearbyRequest(
        latitude=12.6,
        longitude=100.2,
        radius_m=50_000,
        place_types=[PlaceType.MOSQUE],
        limit=20,
    )

    async with SessionLocal() as session:
        rows = await find_nearby_places(session, request)

    assert rows
    assert {row["place_type"] for row in rows} == {"MOSQUE"}


@pytest.mark.asyncio
async def test_along_route_orders_places_by_route_progress() -> None:
    route = RouteResult(
        coordinates=[
            [99.85, 11.45],
            [100.00, 11.95],
            [100.20, 12.60],
            [100.50, 13.50],
        ],
        distance_m=250_000,
        duration_s=10_000,
    )

    async with SessionLocal() as session:
        rows = await find_places_along_route(
            session=session,
            route=route,
            corridor_radius_m=35_000,
            place_types=None,
            limit=20,
        )

    slugs = [row["slug"] for row in rows]

    assert "test-route-far-away" not in slugs
    expected = [
        "test-route-restaurant-south",
        "test-route-mosque-middle",
        "test-route-accommodation-north",
    ]
    filtered = [slug for slug in slugs if slug in expected]
    assert filtered == expected

    progress = [
        row["route_progress"]
        for row in rows
        if row["slug"] in expected
    ]
    assert progress == sorted(progress)


@pytest.mark.asyncio
async def test_reviewed_import_is_idempotent_for_same_verification() -> None:
    place = ReviewedPlace(
        slug="test-import-idempotent",
        name_th="TEST import idempotent",
        name_en=None,
        place_type="RESTAURANT",
        latitude=13.0,
        longitude=100.0,
        address=None,
        district=None,
        province="TEST",
        postal_code=None,
        phone=None,
        website_url=None,
        social_url=None,
        trust_status="UNVERIFIED",
        source_type="FIELD_CHECK",
        source_reference="synthetic://idempotent",
        verified_at=datetime.fromisoformat("2026-09-24T00:00:00+07:00"),
        expires_at=None,
        review_note="Integration test only",
    )

    await apply_places([place])
    await apply_places([place])

    async with SessionLocal() as session:
        count = await session.scalar(
            text(
                """
                SELECT count(*)
                FROM place_verifications pv
                JOIN places p ON p.id = pv.place_id
                WHERE p.slug = :slug
                  AND pv.source_reference = :source_reference
                """
            ),
            {
                "slug": place.slug,
                "source_reference": place.source_reference,
            },
        )

    assert count == 1


@pytest.mark.asyncio
async def test_candidate_can_be_reviewed_and_promoted() -> None:
    candidate_input = Candidate(
        name="TEST promoted candidate",
        place_type="RESTAURANT",
        address="TEST address",
        district="TEST district",
        province="TEST",
        phone=None,
        latitude=None,
        longitude=None,
        proposed_trust_status="UNVERIFIED",
        source_type="FIELD_CHECK",
        source_reference="synthetic://candidate-promotion",
        external_provider="synthetic",
        external_id="candidate-promotion-1",
        certification_number=None,
        certification_expires_at=None,
        review_state="DISCOVERED",
        review_note="Integration test only",
    )
    await apply_candidates([candidate_input])

    async with SessionLocal() as session:
        rows = await list_candidates(
            session,
            review_state=CandidateReviewState.DISCOVERED,
            limit=100,
        )
        candidate = next(
            row
            for row in rows
            if row["external_id"] == candidate_input.external_id
        )

        reviewed = await update_candidate_review(
            session=session,
            candidate_id=candidate["id"],
            latitude=13.25,
            longitude=100.25,
            review_state=CandidateReviewState.APPROVED,
            review_note="Coordinates checked by integration test",
        )

        place_id = await promote_candidate(
            session=session,
            candidate=reviewed,
            slug="test-promoted-candidate",
            name_th="TEST promoted candidate",
        )
        await session.commit()

    assert place_id

    async with SessionLocal() as session:
        place = await find_place_by_slug(session, "test-promoted-candidate")
        candidate_after = await get_candidate(session, candidate["id"])

    assert place is not None
    assert place["province"] == "TEST"
    assert place["trust_status"] == "UNVERIFIED"
    assert candidate_after is not None
    assert candidate_after["review_state"] == "PROMOTED"


@pytest.mark.asyncio
async def test_expired_verification_is_flagged() -> None:
    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                UPDATE place_verifications
                SET expires_at = now() - interval '1 day'
                WHERE place_id = (
                    SELECT id
                    FROM places
                    WHERE slug = 'test-route-restaurant-south'
                )
                """
            )
        )
        await session.commit()

        rows = await find_nearby_places(
            session,
            NearbyRequest(
                latitude=11.8,
                longitude=99.95,
                radius_m=5000,
                limit=10,
            ),
        )

    row = next(item for item in rows if item["slug"] == "test-route-restaurant-south")
    assert row["verification_expired"] is True
