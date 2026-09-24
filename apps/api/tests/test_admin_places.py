import os

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.integration

if os.getenv("RUN_INTEGRATION") != "1":
    pytest.skip("PostGIS integration tests are disabled", allow_module_level=True)

from app.admin_places import get_admin_place, list_admin_places, update_admin_place
from app.db import SessionLocal


@pytest.mark.asyncio
async def test_admin_place_can_be_edited_and_soft_deactivated() -> None:
    async with SessionLocal() as session:
        place_id = (
            await session.execute(
                text(
                    """
                    SELECT id::text
                    FROM places
                    WHERE slug = 'test-route-restaurant-south'
                    """
                )
            )
        ).scalar_one()

        updated = await update_admin_place(
            session,
            place_id,
            {
                "name_th": "TEST ร้านอาหาร จุดใต้ แก้ไข",
                "latitude": 11.801,
                "longitude": 99.951,
                "active": False,
            },
        )
        await session.commit()

        assert updated is not None
        assert updated["name_th"].endswith("แก้ไข")
        assert updated["active"] is False
        assert updated["latitude"] == pytest.approx(11.801)
        assert updated["longitude"] == pytest.approx(99.951)

        fetched = await get_admin_place(session, place_id)
        assert fetched is not None
        assert fetched["active"] is False

        active_only = await list_admin_places(
            session,
            include_inactive=False,
            limit=100,
        )
        assert all(row["id"] != place_id for row in active_only)


@pytest.mark.asyncio
async def test_admin_place_coordinate_update_requires_pair() -> None:
    async with SessionLocal() as session:
        place_id = (
            await session.execute(
                text(
                    """
                    SELECT id::text
                    FROM places
                    WHERE slug = 'test-route-mosque-middle'
                    """
                )
            )
        ).scalar_one()

        with pytest.raises(ValueError, match="updated together"):
            await update_admin_place(
                session,
                place_id,
                {"latitude": 12.7},
            )
