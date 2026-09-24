from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def add_place_verification(
    session: AsyncSession,
    *,
    place_id: str,
    trust_status: str,
    source_type: str,
    source_reference: str | None,
    verified_at: datetime,
    expires_at: datetime | None,
    note: str | None,
) -> str:
    result = await session.execute(
        text(
            """
            INSERT INTO place_verifications (
                place_id,
                claim_type,
                trust_status,
                source_type,
                source_reference,
                verified_at,
                expires_at,
                note,
                verified_by
            )
            VALUES (
                CAST(:place_id AS uuid),
                'MUSLIM_TRAVEL_STATUS',
                CAST(:trust_status AS trust_status),
                CAST(:source_type AS verification_source_type),
                :source_reference,
                :verified_at,
                :expires_at,
                :note,
                'ADMIN'
            )
            RETURNING id::text
            """
        ),
        {
            "place_id": place_id,
            "trust_status": trust_status,
            "source_type": source_type,
            "source_reference": source_reference,
            "verified_at": verified_at,
            "expires_at": expires_at,
            "note": note,
        },
    )
    return result.scalar_one()


async def list_place_verifications(
    session: AsyncSession,
    place_id: str,
) -> list[dict]:
    rows = (
        await session.execute(
            text(
                """
                SELECT
                    id::text,
                    trust_status::text,
                    source_type::text,
                    source_reference,
                    verified_at,
                    expires_at,
                    note,
                    verified_by,
                    created_at
                FROM place_verifications
                WHERE place_id = CAST(:place_id AS uuid)
                  AND claim_type = 'MUSLIM_TRAVEL_STATUS'
                ORDER BY verified_at DESC NULLS LAST, created_at DESC
                """
            ),
            {"place_id": place_id},
        )
    ).mappings().all()
    return [dict(row) for row in rows]
