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
        "--type",
        action="append",
        dest="place_types",
        choices=[item.value for item in PlaceType],
        help="Repeat to restrict place types.",
    )
    return parser


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

    for row in rows:
        progress = float(row["route_progress"] or 0) * 100
        distance = float(row["distance_m"] or 0) / 1000
        trust = row["trust_status"] or "UNVERIFIED"
        expired = " EXPIRED" if row["verification_expired"] else ""
        print(
            f"{progress:5.1f}% | {distance:5.1f} km from route | "
            f"{row['place_type']:<13} | {row['name_th']} | {trust}{expired}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))
