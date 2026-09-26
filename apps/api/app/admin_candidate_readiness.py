from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .pilot import PILOT_PROVINCES


async def load_candidate_readiness(session: AsyncSession) -> list[dict]:
    rows = (
        await session.execute(
            text(
                """
                SELECT
                    province,
                    count(*) FILTER (
                        WHERE place_type::text = 'RESTAURANT'
                    ) AS restaurants,
                    count(*) FILTER (
                        WHERE place_type::text = 'MOSQUE'
                    ) AS mosques,
                    count(*) FILTER (
                        WHERE place_type::text = 'ACCOMMODATION'
                    ) AS accommodation,
                    count(*) FILTER (
                        WHERE review_state::text = 'GEOCODED'
                    ) AS geocoded,
                    count(*) FILTER (
                        WHERE review_state::text = 'APPROVED'
                    ) AS approved,
                    count(*) FILTER (
                        WHERE review_state::text = 'PROMOTED'
                    ) AS promoted
                FROM place_candidates
                WHERE review_state::text <> 'REJECTED'
                  AND province = ANY(:provinces)
                GROUP BY province
                """
            ),
            {"provinces": list(PILOT_PROVINCES)},
        )
    ).mappings().all()

    by_province = {row["province"]: row for row in rows}
    return [
        {
            "province": province,
            "restaurants": int(by_province.get(province, {}).get("restaurants", 0)),
            "mosques": int(by_province.get(province, {}).get("mosques", 0)),
            "accommodation": int(
                by_province.get(province, {}).get("accommodation", 0)
            ),
            "geocoded": int(by_province.get(province, {}).get("geocoded", 0)),
            "approved": int(by_province.get(province, {}).get("approved", 0)),
            "promoted": int(by_province.get(province, {}).get("promoted", 0)),
        }
        for province in PILOT_PROVINCES
    ]


def candidate_readiness_passes(items: list[dict]) -> bool:
    route_ready = all(
        item["restaurants"] > 0 and item["mosques"] > 0
        for item in items
    )
    accommodation_provinces = sum(
        1 for item in items if item["accommodation"] > 0
    )
    return route_ready and accommodation_provinces >= 2
