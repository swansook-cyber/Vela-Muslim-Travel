from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

ADMIN_PLACE_COLUMNS = """
    id::text,
    slug,
    place_type::text,
    name_th,
    name_en,
    address,
    district,
    province,
    phone,
    website_url,
    social_url,
    active,
    ST_Y(location::geometry) AS latitude,
    ST_X(location::geometry) AS longitude,
    created_at,
    updated_at
"""


async def list_admin_places(
    session: AsyncSession,
    *,
    include_inactive: bool = True,
    limit: int = 200,
) -> list[dict]:
    rows = (
        await session.execute(
            text(
                f"""
                SELECT {ADMIN_PLACE_COLUMNS}
                FROM places
                WHERE (:include_inactive OR active = true)
                ORDER BY updated_at DESC
                LIMIT :limit
                """
            ),
            {
                "include_inactive": include_inactive,
                "limit": limit,
            },
        )
    ).mappings().all()
    return [dict(row) for row in rows]


async def get_admin_place(
    session: AsyncSession,
    place_id: str,
) -> dict | None:
    row = (
        await session.execute(
            text(
                f"""
                SELECT {ADMIN_PLACE_COLUMNS}
                FROM places
                WHERE id = CAST(:place_id AS uuid)
                """
            ),
            {"place_id": place_id},
        )
    ).mappings().first()
    return dict(row) if row else None


async def update_admin_place(
    session: AsyncSession,
    place_id: str,
    changes: dict,
) -> dict | None:
    if ("slug" in changes and changes["slug"] is None) or (
        "name_th" in changes and changes["name_th"] is None
    ):
        raise ValueError("Production slug and name_th cannot be null")

    if ("latitude" in changes or "longitude" in changes) and (
        changes.get("latitude") is None or changes.get("longitude") is None
    ):
        raise ValueError("Latitude and longitude must be non-null")

    allowed = {
        "slug",
        "name_th",
        "name_en",
        "address",
        "district",
        "province",
        "phone",
        "website_url",
        "social_url",
        "active",
    }
    assignments: list[str] = []
    params: dict = {"place_id": place_id}

    for field, value in changes.items():
        if field in allowed:
            assignments.append(f"{field} = :{field}")
            params[field] = value

    latitude_present = "latitude" in changes
    longitude_present = "longitude" in changes
    if latitude_present or longitude_present:
        if not (latitude_present and longitude_present):
            raise ValueError("Latitude and longitude must be updated together")
        assignments.append(
            "location = ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography"
        )
        params["latitude"] = changes["latitude"]
        params["longitude"] = changes["longitude"]

    if not assignments:
        return await get_admin_place(session, place_id)

    assignments.append("updated_at = now()")
    sql = text(
        f"""
        UPDATE places
        SET {", ".join(assignments)}
        WHERE id = CAST(:place_id AS uuid)
        RETURNING {ADMIN_PLACE_COLUMNS}
        """
    )
    row = (await session.execute(sql, params)).mappings().first()
    return dict(row) if row else None
