import os

import pytest

pytestmark = pytest.mark.integration

if os.getenv("RUN_INTEGRATION") != "1":
    pytest.skip("PostGIS integration tests are disabled", allow_module_level=True)

from app.admin_candidate_readiness import (
    candidate_readiness_passes,
    load_candidate_readiness,
)
from app.admin_review_progress import load_candidate_review_progress
from app.db import SessionLocal


@pytest.mark.asyncio
async def test_staged_candidate_corridor_is_ready_for_manual_review() -> None:
    async with SessionLocal() as session:
        rows = await load_candidate_readiness(session)

    assert len(rows) == 7
    assert candidate_readiness_passes(rows)

    for row in rows:
        assert row["restaurants"] >= 1
        assert row["mosques"] >= 1


def test_candidate_readiness_requires_two_accommodation_provinces() -> None:
    rows = [
        {
            "province": f"P{i}",
            "restaurants": 1,
            "mosques": 1,
            "accommodation": 1 if i == 0 else 0,
            "geocoded": 0,
            "approved": 0,
            "promoted": 0,
        }
        for i in range(7)
    ]

    assert not candidate_readiness_passes(rows)


@pytest.mark.asyncio
async def test_imported_pilot_queue_remains_blocked_until_manual_review() -> None:
    async with SessionLocal() as session:
        progress = await load_candidate_review_progress(session)

    assert progress["pending"] >= 23
    assert progress["ready_to_approve"] == 0
    assert progress["blocked"] == progress["pending"]
    assert progress["coordinate_pending"] == progress["pending"]
    assert progress["manual_hold"] >= 7
