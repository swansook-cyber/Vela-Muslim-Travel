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

    assert candidate_count >= 18
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


@pytest.mark.asyncio
async def test_admin_dashboard_counts_staged_candidates() -> None:
    from app.admin_queries import get_admin_dashboard

    async with SessionLocal() as session:
        dashboard = await get_admin_dashboard(session)

    assert dashboard["candidates_total"] >= 18
    assert dashboard["discovered"] >= 18
    assert dashboard["production_places"] >= 4


@pytest.mark.asyncio
async def test_candidate_reimport_preserves_review_progress() -> None:
    from pathlib import Path

    from app.tools.import_candidates import apply_candidates, load_candidates

    candidate_path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    candidates = load_candidates(candidate_path)
    target = candidates[0]

    async with SessionLocal() as session:
        await session.execute(
            text(
                """
                UPDATE place_candidates
                SET
                    latitude = 13.750000,
                    longitude = 100.500000,
                    review_state = 'GEOCODED',
                    review_note = 'manual reviewed coordinates'
                WHERE external_provider = :provider
                  AND external_id = :external_id
                """
            ),
            {
                "provider": target.external_provider,
                "external_id": target.external_id,
            },
        )
        await session.commit()

    await apply_candidates(candidates)

    async with SessionLocal() as session:
        row = (
            await session.execute(
                text(
                    """
                    SELECT latitude, longitude, review_state::text, review_note
                    FROM place_candidates
                    WHERE external_provider = :provider
                      AND external_id = :external_id
                    """
                ),
                {
                    "provider": target.external_provider,
                    "external_id": target.external_id,
                },
            )
        ).mappings().one()

    assert row["latitude"] == pytest.approx(13.75)
    assert row["longitude"] == pytest.approx(100.5)
    assert row["review_state"] == "GEOCODED"
    assert row["review_note"] == "manual reviewed coordinates"


@pytest.mark.asyncio
async def test_admin_audit_log_records_review_action() -> None:
    from app.admin_queries import list_admin_audit, log_admin_action

    async with SessionLocal() as session:
        await log_admin_action(
            session,
            action="TEST_REVIEW",
            entity_type="place_candidate",
            entity_id="integration-test",
            details={"state": "GEOCODED"},
        )
        await session.commit()

        rows = await list_admin_audit(session, limit=10)

    assert any(
        row["action"] == "TEST_REVIEW"
        and row["entity_id"] == "integration-test"
        for row in rows
    )
