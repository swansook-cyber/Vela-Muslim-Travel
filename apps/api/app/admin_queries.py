import json

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
    review_hold_reason,
    created_at,
    updated_at
"""


async def list_candidates(
    session: AsyncSession,
    review_state: CandidateReviewState | None,
    province: str | None = None,
    place_type: str | None = None,
    limit: int = 100,
) -> list[dict]:
    sql = text(
        f"""
        SELECT {CANDIDATE_COLUMNS}
        FROM place_candidates
        WHERE (
            CAST(:review_state AS text) IS NULL
            OR review_state::text = CAST(:review_state AS text)
        )
          AND (
            CAST(:province AS text) IS NULL
            OR province = CAST(:province AS text)
          )
          AND (
            CAST(:place_type AS text) IS NULL
            OR place_type::text = CAST(:place_type AS text)
          )
        ORDER BY
            CASE province
                WHEN 'นครศรีธรรมราช' THEN 1
                WHEN 'สุราษฎร์ธานี' THEN 2
                WHEN 'ชุมพร' THEN 3
                WHEN 'ประจวบคีรีขันธ์' THEN 4
                WHEN 'เพชรบุรี' THEN 5
                WHEN 'สระบุรี' THEN 6
                WHEN 'นครราชสีมา' THEN 7
                ELSE 99
            END,
            updated_at DESC
        LIMIT :limit
        """
    )
    rows = (
        await session.execute(
            sql,
            {
                "review_state": review_state.value if review_state else None,
                "province": province,
                "place_type": place_type,
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
    review_hold_reason: str | None,
) -> dict:
    sql = text(
        f"""
        UPDATE place_candidates
        SET
            latitude = :latitude,
            longitude = :longitude,
            review_state = CAST(:review_state AS candidate_review_state),
            review_note = :review_note,
            review_hold_reason = :review_hold_reason,
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
                "review_hold_reason": review_hold_reason,
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
    duplicate = (
        await session.execute(
            text(
                """
                SELECT
                    id::text,
                    slug,
                    name_th,
                    ST_Distance(
                        location,
                        ST_SetSRID(
                            ST_MakePoint(:longitude, :latitude),
                            4326
                        )::geography
                    ) AS distance_m
                FROM places
                WHERE active = true
                  AND place_type::text = :place_type
                  AND ST_DWithin(
                        location,
                        ST_SetSRID(
                            ST_MakePoint(:longitude, :latitude),
                            4326
                        )::geography,
                        150
                  )
                ORDER BY distance_m
                LIMIT 1
                """
            ),
            {
                "longitude": candidate["longitude"],
                "latitude": candidate["latitude"],
                "place_type": candidate["place_type"],
            },
        )
    ).mappings().first()

    if duplicate is not None:
        raise ValueError(
            "Potential duplicate place within 150 m: "
            f"{duplicate['name_th']} ({duplicate['slug']})"
        )

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
        ON CONFLICT (slug) DO NOTHING
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
    place_id = result.scalar_one_or_none()
    if place_id is None:
        raise ValueError(f"Production slug already exists: {slug}")

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

    await session.execute(
        text(
            """
            UPDATE place_candidates
            SET
                review_state = 'PROMOTED',
                updated_at = now()
            WHERE id = CAST(:candidate_id AS uuid)
            """
        ),
        {"candidate_id": candidate["id"]},
    )

    return str(place_id)


async def get_admin_dashboard(session: AsyncSession) -> dict:
    sql = text(
        """
        SELECT
            (SELECT count(*) FROM place_candidates) AS candidates_total,
            (
                SELECT count(*) FROM place_candidates
                WHERE review_state = 'DISCOVERED'
            ) AS discovered,
            (
                SELECT count(*) FROM place_candidates
                WHERE review_state = 'GEOCODED'
            ) AS geocoded,
            (
                SELECT count(*) FROM place_candidates
                WHERE review_state = 'APPROVED'
            ) AS approved,
            (
                SELECT count(*) FROM place_candidates
                WHERE review_state = 'PROMOTED'
            ) AS promoted,
            (
                SELECT count(*) FROM place_candidates
                WHERE review_state = 'REJECTED'
            ) AS rejected,
            (SELECT count(*) FROM places WHERE active = true) AS production_places,
            (
                SELECT count(*)
                FROM place_verifications
                WHERE expires_at IS NOT NULL
                  AND expires_at < now()
            ) AS expired_verifications,
            (
                SELECT count(*)
                FROM place_verifications
                WHERE expires_at IS NOT NULL
                  AND expires_at >= now()
                  AND expires_at < now() + interval '30 days'
            ) AS certifications_expiring_30d
        """
    )
    row = (await session.execute(sql)).mappings().one()
    return dict(row)


async def log_admin_action(
    session: AsyncSession,
    *,
    action: str,
    entity_type: str,
    entity_id: str | None,
    details: dict | None = None,
) -> None:
    await session.execute(
        text(
            """
            INSERT INTO admin_audit_log (
                action,
                entity_type,
                entity_id,
                details
            )
            VALUES (
                :action,
                :entity_type,
                :entity_id,
                CAST(:details AS jsonb)
            )
            """
        ),
        {
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": json.dumps(details or {}, ensure_ascii=False),
        },
    )


async def list_admin_audit(
    session: AsyncSession,
    limit: int = 50,
) -> list[dict]:
    rows = (
        await session.execute(
            text(
                """
                SELECT
                    id::text,
                    action,
                    entity_type,
                    entity_id,
                    details,
                    created_at
                FROM admin_audit_log
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        )
    ).mappings().all()
    return [dict(row) for row in rows]
