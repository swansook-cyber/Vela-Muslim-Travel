import os

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.integration

if os.getenv("RUN_INTEGRATION") != "1":
    pytest.skip("PostGIS integration tests are disabled", allow_module_level=True)

from app.admin_places import get_admin_place, update_admin_place
from app.admin_queries import list_admin_audit, log_admin_action
from app.db import SessionLocal


@pytest.mark.asyncio
async def test_place_update_can_be_audited() -> None:
    async with SessionLocal() as session:
        original = (
            await session.execute(
                text(
                    """
                    SELECT id::text, phone
                    FROM places
                    WHERE slug = 'test-route-accommodation-north'
                    """
                )
            )
        ).mappings().one()
        place_id = original["id"]

        try:
            row = await update_admin_place(
                session,
                place_id,
                {"phone": "+66 00 000 0000"},
            )
            assert row is not None

            await log_admin_action(
                session,
                action="TEST_UPDATE_PLACE",
                entity_type="place",
                entity_id=place_id,
                details={"changed_fields": ["phone"]},
            )
            await session.commit()

            fetched = await get_admin_place(session, place_id)
            audit = await list_admin_audit(session, limit=20)

            assert fetched is not None
            assert fetched["phone"] == "+66 00 000 0000"
            assert any(
                item["action"] == "TEST_UPDATE_PLACE"
                and item["entity_id"] == place_id
                for item in audit
            )
        finally:
            await update_admin_place(
                session,
                place_id,
                {"phone": original["phone"]},
            )
            await session.commit()
