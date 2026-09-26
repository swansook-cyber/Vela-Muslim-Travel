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
                    """
                )
            )
        ).scalar_one()

        google_discovery_count = (
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

    assert candidate_count >= 24
    assert google_discovery_count >= 12
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

    assert dashboard["candidates_total"] >= 24
    assert dashboard["geocoded"] >= 5
    assert (
        dashboard["discovered"]
        + dashboard["geocoded"]
        + dashboard["approved"]
        + dashboard["promoted"]
        + dashboard["rejected"]
        == dashboard["candidates_total"]
    )
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
                    review_note = 'manual reviewed coordinates',
                    coordinate_checked_at = now()
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
                    SELECT
                        latitude,
                        longitude,
                        review_state::text,
                        review_note,
                        coordinate_checked_at
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
    assert row["coordinate_checked_at"] is not None


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


@pytest.mark.asyncio
async def test_list_candidates_pilot_only_filters_before_return() -> None:
    from app.admin_queries import list_candidates
    from app.admin_schemas import CandidateReviewState
    from app.tools.candidate_queue_readiness import PILOT_PROVINCES

    async with SessionLocal() as session:
        rows = await list_candidates(
            session,
            review_state=CandidateReviewState.DISCOVERED,
            province=None,
            place_type=None,
            pilot_only=True,
            limit=500,
        )

    assert rows
    assert all(row["province"] in PILOT_PROVINCES for row in rows)
    assert all(row["province"] != "กรุงเทพมหานคร" for row in rows)
