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
