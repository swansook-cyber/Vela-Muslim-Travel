import os

import pytest

from app.db import SessionLocal
from app.queries import find_nearby_places, find_place_by_slug, find_places_along_route
from app.routing import RouteResult
from app.schemas import NearbyRequest, PlaceType
from app.tools.import_reviewed_places import ReviewedPlace, apply_places
from sqlalchemy import text

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
        verified_at="2026-09-24T00:00:00+07:00",
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
