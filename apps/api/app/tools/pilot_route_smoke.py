from __future__ import annotations

import asyncio

from app.db import SessionLocal
from app.queries import find_places_along_route
from app.routing import get_route
from app.schemas import Coordinate, PlaceType
from app.tools.route_smoke import summarize_rows

PILOT_ORIGIN = Coordinate(latitude=8.16, longitude=99.68)
PILOT_DESTINATION = Coordinate(latitude=14.53, longitude=101.37)
PILOT_CORRIDORS_KM = (2, 5, 10)


async def async_main() -> int:
    route = await get_route(PILOT_ORIGIN, PILOT_DESTINATION)

    print(
        f"Pilot route: {route.distance_m / 1000:.1f} km, "
        f"{route.duration_s / 3600:.1f} h"
    )

    overall_ready = False
    async with SessionLocal() as session:
        for corridor_km in PILOT_CORRIDORS_KM:
            rows = await find_places_along_route(
                session=session,
                route=route,
                corridor_radius_m=corridor_km * 1000,
                place_types=None,
                limit=200,
            )
            summary = summarize_rows(rows)
            counts = summary["counts"]
            core = "PASS" if summary["core_ready"] else "GAPS"
            print(
                f"{corridor_km:>2} km | total={len(rows):>3} | "
                f"restaurant={counts[PlaceType.RESTAURANT.value]:>2} | "
                f"mosque={counts[PlaceType.MOSQUE.value]:>2} | "
                f"prayer_room={counts[PlaceType.PRAYER_ROOM.value]:>2} | "
                f"accommodation={counts[PlaceType.ACCOMMODATION.value]:>2} | "
                f"provinces={len(summary['provinces']):>2} | "
                f"expired={summary['expired']:>2} | core={core}"
            )
            if corridor_km == 5 and summary["core_ready"]:
                overall_ready = True

    if not overall_ready:
        print(
            "Pilot mechanical gate: FAIL "
            "(5 km corridor is missing food, prayer, or accommodation coverage)"
        )
        return 2

    print("Pilot mechanical gate: PASS at 5 km")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))
