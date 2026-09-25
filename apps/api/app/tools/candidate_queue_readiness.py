from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

PILOT_PROVINCES = (
    "นครศรีธรรมราช",
    "สุราษฎร์ธานี",
    "ชุมพร",
    "ประจวบคีรีขันธ์",
    "เพชรบุรี",
    "สระบุรี",
    "นครราชสีมา",
)

REQUIRED_ROUTE_TYPES = ("RESTAURANT", "MOSQUE")


def load_candidate_counts(path: Path) -> dict[str, Counter[str]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("review_state", "DISCOVERED").strip().upper() == "REJECTED":
                continue
            province = row.get("province", "").strip()
            place_type = row.get("place_type", "").strip().upper()
            if province and place_type:
                counts[province][place_type] += 1

    return counts


def candidate_queue_passes(counts: dict[str, Counter[str]]) -> bool:
    route_types_ready = all(
        all(counts[province][place_type] > 0 for place_type in REQUIRED_ROUTE_TYPES)
        for province in PILOT_PROVINCES
    )
    accommodation_provinces = sum(
        1
        for province in PILOT_PROVINCES
        if counts[province]["ACCOMMODATION"] > 0
    )
    return route_types_ready and accommodation_provinces >= 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check discovery-candidate coverage for the Phase 0 pilot corridor."
    )
    parser.add_argument("csv_path", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    counts = load_candidate_counts(args.csv_path)

    print("Vela Muslim Travel candidate queue coverage")
    print("------------------------------------------")
    for province in PILOT_PROVINCES:
        province_counts = counts[province]
        missing = [
            place_type
            for place_type in REQUIRED_ROUTE_TYPES
            if province_counts[place_type] == 0
        ]
        print(
            f"{province}: restaurant={province_counts['RESTAURANT']} "
            f"mosque={province_counts['MOSQUE']} "
            f"accommodation={province_counts['ACCOMMODATION']} "
            f"missing_route_types={','.join(missing) or '-'}"
        )

    accommodation_provinces = sum(
        1
        for province in PILOT_PROVINCES
        if counts[province]["ACCOMMODATION"] > 0
    )
    print(f"Accommodation provinces: {accommodation_provinces}")

    if not candidate_queue_passes(counts):
        print("Candidate queue is not ready for full corridor review.")
        return 2

    print("Candidate queue is ready for manual coordinate/evidence review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
