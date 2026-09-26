from __future__ import annotations

import asyncio
from dataclasses import dataclass

from sqlalchemy import text

from app.db import SessionLocal

PILOT_PROVINCES = (
    "นครศรีธรรมราช",
    "สุราษฎร์ธานี",
    "ชุมพร",
    "ประจวบคีรีขันธ์",
    "เพชรบุรี",
    "สระบุรี",
    "นครราชสีมา",
)

CORE_PLACE_TYPES = (
    "RESTAURANT",
    "MOSQUE",
    "ACCOMMODATION",
)


@dataclass(slots=True)
class ProvinceReadiness:
    province: str
    restaurants: int
    mosques: int
    accommodation: int

    @property
    def total(self) -> int:
        return self.restaurants + self.mosques + self.accommodation

    @property
    def missing_types(self) -> list[str]:
        missing: list[str] = []
        if self.restaurants == 0:
            missing.append("RESTAURANT")
        if self.mosques == 0:
            missing.append("MOSQUE")
        if self.accommodation == 0:
            missing.append("ACCOMMODATION")
        return missing


async def load_readiness() -> list[ProvinceReadiness]:
    sql = text(
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
            ) AS accommodation
        FROM places
        WHERE active = true
          AND COALESCE(source_status, '') <> 'TEST_FIXTURE'
          AND province = ANY(:provinces)
        GROUP BY province
        """
    )

    async with SessionLocal() as session:
        rows = (
            await session.execute(sql, {"provinces": list(PILOT_PROVINCES)})
        ).mappings().all()

    by_province = {row["province"]: row for row in rows}
    return [
        ProvinceReadiness(
            province=province,
            restaurants=int(by_province.get(province, {}).get("restaurants", 0)),
            mosques=int(by_province.get(province, {}).get("mosques", 0)),
            accommodation=int(by_province.get(province, {}).get("accommodation", 0)),
        )
        for province in PILOT_PROVINCES
    ]


def readiness_passes(items: list[ProvinceReadiness]) -> bool:
    route_ready = all(
        item.restaurants > 0 and item.mosques > 0
        for item in items
    )
    accommodation_provinces = sum(
        1 for item in items if item.accommodation > 0
    )
    return route_ready and accommodation_provinces >= 2


async def async_main() -> int:
    items = await load_readiness()

    print("Vela Muslim Travel pilot readiness")
    print("--------------------------------")

    for item in items:
        missing = ", ".join(item.missing_types) or "-"
        print(
            f"{item.province}: total={item.total} "
            f"restaurant={item.restaurants} mosque={item.mosques} "
            f"accommodation={item.accommodation} category_gaps={missing}"
        )

    accommodation_provinces = sum(
        1 for item in items if item.accommodation > 0
    )
    print(
        f"Accommodation coverage: {accommodation_provinces}/2 "
        "target provinces minimum"
    )

    if not readiness_passes(items):
        print()
        print(
            "Pilot is not ready: every target province needs at least one "
            "restaurant and mosque, with accommodation in at least two provinces."
        )
        return 2

    print()
    print(
        "Pilot production coverage meets the structural gate: restaurant and "
        "mosque in every target province, accommodation in at least two provinces."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))
