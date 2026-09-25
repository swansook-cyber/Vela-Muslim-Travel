import os

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.integration

if os.getenv("RUN_INTEGRATION") != "1":
    pytest.skip("PostGIS integration tests are disabled", allow_module_level=True)

from app.db import SessionLocal
from app.migrations import run_migrations


@pytest.mark.asyncio
async def test_migration_runner_is_idempotent() -> None:
    first = await run_migrations()
    second = await run_migrations()

    assert "0001_baseline" in first or first == []
    assert second == []

    async with SessionLocal() as session:
        count = (
            await session.execute(
                text(
                    """
                    SELECT count(*)
                    FROM schema_migrations
                    WHERE version = '0001_baseline'
                    """
                )
            )
        ).scalar_one()

    assert count == 1


@pytest.mark.asyncio
async def test_admin_audit_migration_is_recorded() -> None:
    await run_migrations()

    async with SessionLocal() as session:
        count = (
            await session.execute(
                text(
                    """
                    SELECT count(*)
                    FROM schema_migrations
                    WHERE version = '0002_admin_audit_log'
                    """
                )
            )
        ).scalar_one()

    assert count == 1


@pytest.mark.asyncio
async def test_candidate_review_hold_migration_is_recorded() -> None:
    await run_migrations()

    async with SessionLocal() as session:
        count = (
            await session.execute(
                text(
                    """
                    SELECT count(*)
                    FROM schema_migrations
                    WHERE version = '0003_candidate_review_hold'
                    """
                )
            )
        ).scalar_one()

        column_count = (
            await session.execute(
                text(
                    """
                    SELECT count(*)
                    FROM information_schema.columns
                    WHERE table_name = 'place_candidates'
                      AND column_name = 'review_hold_reason'
                    """
                )
            )
        ).scalar_one()

    assert count == 1
    assert column_count == 1


@pytest.mark.asyncio
async def test_candidate_source_checked_at_migration_is_recorded() -> None:
    await run_migrations()

    async with SessionLocal() as session:
        count = (
            await session.execute(
                text(
                    """
                    SELECT count(*)
                    FROM schema_migrations
                    WHERE version = '0004_candidate_source_checked_at'
                    """
                )
            )
        ).scalar_one()

        column_count = (
            await session.execute(
                text(
                    """
                    SELECT count(*)
                    FROM information_schema.columns
                    WHERE table_name = 'place_candidates'
                      AND column_name = 'source_checked_at'
                    """
                )
            )
        ).scalar_one()

    assert count == 1
    assert column_count == 1
