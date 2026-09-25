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
    return all(item.total > 0 for item in items)


async def async_main() -> int:
    items = await load_readiness()

    print("Vela Muslim Travel pilot readiness")
    print("--------------------------------")

    for item in items:
        missing = ", ".join(item.missing_types) or "-"
        print(
            f"{item.province}: total={item.total} "
            f"restaurant={item.restaurants} mosque={item.mosques} "
            f"accommodation={item.accommodation} missing={missing}"
        )

    if not readiness_passes(items):
        print()
        print("Pilot is not ready: at least one corridor province has no production place.")
        return 2

    print()
    print("Pilot corridor has at least one production place in every target province.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))
