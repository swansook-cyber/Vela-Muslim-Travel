import os

import pytest

pytestmark = pytest.mark.integration

if os.getenv("RUN_INTEGRATION") != "1":
    pytest.skip("PostGIS integration tests are disabled", allow_module_level=True)

from sqlalchemy import text

from app.db import SessionLocal


@pytest.mark.asyncio
async def test_real_world_pilot_candidates_are_staged_not_promoted() -> None:
    async with SessionLocal() as session:
        candidate_count = (
            await session.execute(
                text(
                    """
                    SELECT count(*)
                    FROM place_candidates
                    WHERE external_provider IN ('google_business', 'google_places')
                    """
                )
            )
        ).scalar_one()

        promoted_count = (
            await session.execute(
                text(
                    """
                    SELECT count(*)
                    FROM places
                    WHERE source_status = 'CANDIDATE_PROMOTION'
                    """
                )
            )
        ).scalar_one()

    assert candidate_count >= 12
    assert promoted_count == 0


@pytest.mark.asyncio
async def test_official_certification_candidates_keep_official_evidence() -> None:
    async with SessionLocal() as session:
        rows = (
            await session.execute(
                text(
                    """
                    SELECT
                        proposed_trust_status::text,
                        source_type::text,
                        certification_number,
                        source_reference
                    FROM place_candidates
                    WHERE proposed_trust_status::text IN (
                        'HALAL_CERTIFIED',
                        'HALAL_CERTIFIED_SERVICE'
                    )
                    ORDER BY name
                    """
                )
            )
        ).mappings().all()

    assert len(rows) >= 2
    for row in rows:
        assert row["source_type"] == "OFFICIAL_CERTIFICATION"
        assert row["certification_number"]
        assert row["source_reference"]
