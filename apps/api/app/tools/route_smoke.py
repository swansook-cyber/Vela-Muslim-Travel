from __future__ import annotations

import argparse
import asyncio

from app.db import SessionLocal
from app.queries import find_places_along_route
from app.routing import get_route
from app.schemas import Coordinate, PlaceType


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a real routing smoke test against production place data."
    )
    parser.add_argument("--origin-lat", type=float, required=True)
    parser.add_argument("--origin-lng", type=float, required=True)
    parser.add_argument("--destination-lat", type=float, required=True)
    parser.add_argument("--destination-lng", type=float, required=True)
    parser.add_argument("--corridor-km", type=float, default=5.0)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument(
        "--require-core-types",
        action="store_true",
        help=(
            "Exit non-zero unless the corridor contains food, prayer, "
            "and accommodation coverage."
        ),
    )
    parser.add_argument(
        "--type",
        action="append",
        dest="place_types",
        choices=[item.value for item in PlaceType],
        help="Repeat to restrict place types.",
    )
    return parser


def summarize_rows(rows: list[dict]) -> dict:
    counts = {item.value: 0 for item in PlaceType}
    provinces: set[str] = set()
    expired = 0

    for row in rows:
        place_type = str(row["place_type"])
        if place_type in counts:
            counts[place_type] += 1
        if row.get("province"):
            provinces.add(str(row["province"]))
        if row.get("verification_expired"):
            expired += 1

    core = {
        "food": counts[PlaceType.RESTAURANT.value] > 0,
        "prayer": (
            counts[PlaceType.MOSQUE.value] > 0
            or counts[PlaceType.PRAYER_ROOM.value] > 0
        ),
        "accommodation": counts[PlaceType.ACCOMMODATION.value] > 0,
    }
    return {
        "counts": counts,
        "provinces": sorted(provinces),
        "expired": expired,
        "core": core,
        "core_ready": all(core.values()),
    }


async def async_main() -> int:
    args = build_parser().parse_args()

    origin = Coordinate(
        latitude=args.origin_lat,
        longitude=args.origin_lng,
    )
    destination = Coordinate(
        latitude=args.destination_lat,
        longitude=args.destination_lng,
    )
    place_types = (
        [PlaceType(value) for value in args.place_types]
        if args.place_types
        else None
    )

    route = await get_route(origin, destination)

    async with SessionLocal() as session:
        rows = await find_places_along_route(
            session=session,
            route=route,
            corridor_radius_m=int(args.corridor_km * 1000),
            place_types=place_types,
            limit=args.limit,
        )

    print(
        f"Route: {route.distance_m / 1000:.1f} km, "
        f"{route.duration_s / 3600:.1f} h"
    )
    print(f"Places inside {args.corridor_km:g} km corridor: {len(rows)}")

    summary = summarize_rows(rows)
    counts = summary["counts"]
    print(
        "Coverage: "
        f"restaurant={counts[PlaceType.RESTAURANT.value]}, "
        f"mosque={counts[PlaceType.MOSQUE.value]}, "
        f"prayer_room={counts[PlaceType.PRAYER_ROOM.value]}, "
        f"accommodation={counts[PlaceType.ACCOMMODATION.value]}"
    )
    print(
        f"Provinces represented: {len(summary['provinces'])} | "
        f"Expired evidence: {summary['expired']}"
    )
    missing_core = [
        label for label, present in summary["core"].items() if not present
    ]
    if missing_core:
        print("Mechanical core gaps: " + ", ".join(missing_core))
    else:
        print("Mechanical core coverage: PASS")

    for row in rows:
        progress = float(row["route_progress"] or 0) * 100
        distance = float(row["distance_m"] or 0) / 1000
        trust = row["trust_status"] or "UNVERIFIED"
        expired = " EXPIRED" if row["verification_expired"] else ""
        print(
            f"{progress:5.1f}% | {distance:5.1f} km from route | "
            f"{row['place_type']:<13} | {row['name_th']} | {trust}{expired}"
        )

    if args.require_core_types and not summary["core_ready"]:
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))
