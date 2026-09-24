from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .admin_schemas import CandidateReviewState

CANDIDATE_COLUMNS = """
    id::text,
    name,
    place_type::text,
    address,
    district,
    province,
    phone,
    latitude,
    longitude,
    proposed_trust_status::text,
    source_type::text,
    source_reference,
    external_provider,
    external_id,
    certification_number,
    certification_expires_at,
    review_state::text,
    review_note,
    created_at,
    updated_at
"""


async def list_candidates(
    session: AsyncSession,
    review_state: CandidateReviewState | None,
    limit: int = 100,
) -> list[dict]:
    sql = text(
        f"""
        SELECT {CANDIDATE_COLUMNS}
        FROM place_candidates
        WHERE (:review_state IS NULL OR review_state::text = :review_state)
        ORDER BY updated_at DESC
        LIMIT :limit
        """
    )
    rows = (
        await session.execute(
            sql,
            {
                "review_state": review_state.value if review_state else None,
                "limit": limit,
            },
        )
    ).mappings().all()
    return [dict(row) for row in rows]


async def get_candidate(
    session: AsyncSession,
    candidate_id: str,
) -> dict | None:
    sql = text(
        f"""
        SELECT {CANDIDATE_COLUMNS}
        FROM place_candidates
        WHERE id = CAST(:candidate_id AS uuid)
        """
    )
    row = (
        await session.execute(sql, {"candidate_id": candidate_id})
    ).mappings().first()
    return dict(row) if row else None


async def update_candidate_review(
    session: AsyncSession,
    candidate_id: str,
    latitude: float | None,
    longitude: float | None,
    review_state: CandidateReviewState,
    review_note: str | None,
) -> dict:
    sql = text(
        f"""
        UPDATE place_candidates
        SET
            latitude = :latitude,
            longitude = :longitude,
            review_state = CAST(:review_state AS candidate_review_state),
            review_note = :review_note,
            updated_at = now()
        WHERE id = CAST(:candidate_id AS uuid)
        RETURNING {CANDIDATE_COLUMNS}
        """
    )
    row = (
        await session.execute(
            sql,
            {
                "candidate_id": candidate_id,
                "latitude": latitude,
                "longitude": longitude,
                "review_state": review_state.value,
                "review_note": review_note,
            },
        )
    ).mappings().one()
    return dict(row)


async def promote_candidate(
    session: AsyncSession,
    candidate: dict,
    slug: str,
    name_th: str,
) -> str:
    place_sql = text(
        """
        INSERT INTO places (
            slug,
            place_type,
            name_th,
            location,
            address,
            district,
            province,
            phone,
            active,
            source_status,
            updated_at
        )
        VALUES (
            :slug,
            CAST(:place_type AS place_type),
            :name_th,
            ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography,
            :address,
            :district,
            :province,
            :phone,
            true,
            'CANDIDATE_PROMOTION',
            now()
        )
        ON CONFLICT (slug) DO UPDATE SET
            place_type = EXCLUDED.place_type,
            name_th = EXCLUDED.name_th,
            location = EXCLUDED.location,
            address = EXCLUDED.address,
            district = EXCLUDED.district,
            province = EXCLUDED.province,
            phone = EXCLUDED.phone,
            active = true,
            source_status = 'CANDIDATE_PROMOTION',
            updated_at = now()
        RETURNING id
        """
    )
    result = await session.execute(
        place_sql,
        {
            "slug": slug,
            "place_type": candidate["place_type"],
            "name_th": name_th,
            "longitude": candidate["longitude"],
            "latitude": candidate["latitude"],
            "address": candidate["address"],
            "district": candidate["district"],
            "province": candidate["province"],
            "phone": candidate["phone"],
        },
    )
    place_id = result.scalar_one()

    verification_sql = text(
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
        SELECT
            :place_id,
            'MUSLIM_TRAVEL_STATUS',
            CAST(:trust_status AS trust_status),
            CAST(:source_type AS verification_source_type),
            :source_reference,
            now(),
            :expires_at,
            :note,
            'ADMIN_PROMOTION'
        WHERE NOT EXISTS (
            SELECT 1
            FROM place_verifications existing
            WHERE existing.place_id = :place_id
              AND existing.claim_type = 'MUSLIM_TRAVEL_STATUS'
              AND existing.trust_status = CAST(:trust_status AS trust_status)
              AND existing.source_type = CAST(:source_type AS verification_source_type)
              AND existing.source_reference IS NOT DISTINCT FROM :source_reference
              AND existing.expires_at IS NOT DISTINCT FROM :expires_at
        )
        """
    )
    await session.execute(
        verification_sql,
        {
            "place_id": place_id,
            "trust_status": candidate["proposed_trust_status"],
            "source_type": candidate["source_type"],
            "source_reference": candidate["source_reference"],
            "expires_at": candidate["certification_expires_at"],
            "note": candidate["review_note"],
        },
    )

    return str(place_id)
