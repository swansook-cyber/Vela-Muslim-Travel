import os

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.integration

if os.getenv("RUN_INTEGRATION") != "1":
    pytest.skip("PostGIS integration tests are disabled", allow_module_level=True)

from app.admin_queries import check_candidate_promotion
from app.db import SessionLocal


@pytest.mark.asyncio
async def test_promotion_preflight_detects_nearby_duplicate_and_existing_slug() -> None:
    async with SessionLocal() as session:
        existing = (
            await session.execute(
                text(
                    """
                    SELECT
                        slug,
                        place_type::text AS place_type,
                        ST_Y(location::geometry) AS latitude,
                        ST_X(location::geometry) AS longitude
                    FROM places
                    WHERE slug = 'test-route-restaurant-south'
                    """
                )
            )
        ).mappings().one()

        candidate = {
            "latitude": existing["latitude"],
            "longitude": existing["longitude"],
            "place_type": existing["place_type"],
        }

        result = await check_candidate_promotion(
            session,
            candidate,
            existing["slug"],
        )

    assert result["can_promote"] is False
    assert result["slug_exists"] is True
    assert result["duplicate"] is not None
    assert result["duplicate"]["slug"] == existing["slug"]
    assert result["duplicate"]["distance_m"] == pytest.approx(0.0, abs=0.1)


@pytest.mark.asyncio
async def test_promotion_preflight_passes_for_unique_slug_and_remote_point() -> None:
    candidate = {
        "latitude": 18.7883,
        "longitude": 98.9853,
        "place_type": "RESTAURANT",
    }

    async with SessionLocal() as session:
        result = await check_candidate_promotion(
            session,
            candidate,
            "integration-unique-promotion-preflight",
        )

    assert result["can_promote"] is True
    assert result["slug_exists"] is False
    assert result["duplicate"] is None
