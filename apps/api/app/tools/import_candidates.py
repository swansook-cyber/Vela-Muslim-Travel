from __future__ import annotations

import argparse
import asyncio
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

from app.db import SessionLocal
from app.tools.import_reviewed_places import (
    ALLOWED_PLACE_TYPES,
    ALLOWED_SOURCE_TYPES,
    ALLOWED_TRUST_STATUSES,
    CERTIFIED_STATUSES,
    empty_to_none,
    parse_datetime,
)


@dataclass(slots=True)
class Candidate:
    name: str
    place_type: str
    address: str | None
    district: str | None
    province: str | None
    phone: str | None
    latitude: float | None
    longitude: float | None
    proposed_trust_status: str
    source_type: str
    source_reference: str | None
    external_provider: str | None
    external_id: str | None
    certification_number: str | None
    certification_expires_at: datetime | None
    review_state: str
    review_note: str | None
    review_hold_reason: str | None = None


ALLOWED_REVIEW_STATES = {
    "DISCOVERED",
    "GEOCODED",
    "APPROVED",
    "PROMOTED",
    "REJECTED",
}


def parse_candidate(row: dict[str, str], row_number: int) -> Candidate:
    name = row.get("name", "").strip()
    place_type = row.get("place_type", "").strip().upper()
    trust_status = row.get("proposed_trust_status", "").strip().upper()
    source_type = row.get("source_type", "").strip().upper()
    review_state = row.get("review_state", "DISCOVERED").strip().upper()
    source_reference = empty_to_none(row.get("source_reference"))
    external_provider = empty_to_none(row.get("external_provider"))
    external_id = empty_to_none(row.get("external_id"))
    certification_number = empty_to_none(row.get("certification_number"))
    certification_expires_at = parse_datetime(
        row.get("certification_expires_at"),
        "certification_expires_at",
        row_number,
    )

    latitude_raw = empty_to_none(row.get("latitude"))
    longitude_raw = empty_to_none(row.get("longitude"))
    if (latitude_raw is None) != (longitude_raw is None):
        raise ValueError(
            f"Row {row_number}: latitude and longitude must be provided together"
        )

    latitude: float | None = None
    longitude: float | None = None
    if latitude_raw is not None and longitude_raw is not None:
        try:
            latitude = float(latitude_raw)
            longitude = float(longitude_raw)
        except ValueError as exc:
            raise ValueError(
                f"Row {row_number}: latitude/longitude must be numeric"
            ) from exc

        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise ValueError(f"Row {row_number}: coordinates are out of range")

    if not name:
        raise ValueError(f"Row {row_number}: name is required")
    if place_type not in ALLOWED_PLACE_TYPES:
        raise ValueError(f"Row {row_number}: invalid place_type {place_type!r}")
    if trust_status not in ALLOWED_TRUST_STATUSES:
        raise ValueError(f"Row {row_number}: invalid trust status {trust_status!r}")
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError(f"Row {row_number}: invalid source type {source_type!r}")
    if source_type != "UNKNOWN" and not source_reference:
        raise ValueError(
            f"Row {row_number}: non-UNKNOWN source requires source_reference"
        )
    if review_state not in ALLOWED_REVIEW_STATES:
        raise ValueError(f"Row {row_number}: invalid review state {review_state!r}")

    if review_state in {"GEOCODED", "APPROVED", "PROMOTED"} and latitude is None:
        raise ValueError(
            f"Row {row_number}: review state {review_state} requires coordinates"
        )

    if place_type == "ACCOMMODATION" and trust_status == "HALAL_CERTIFIED":
        raise ValueError(
            f"Row {row_number}: accommodation must use HALAL_CERTIFIED_SERVICE"
        )

    if place_type == "RESTAURANT" and trust_status == "HALAL_CERTIFIED_SERVICE":
        raise ValueError(
            f"Row {row_number}: restaurant must use HALAL_CERTIFIED"
        )

    if trust_status in CERTIFIED_STATUSES:
        if source_type != "OFFICIAL_CERTIFICATION" or not source_reference:
            raise ValueError(
                f"Row {row_number}: certified candidate requires official evidence"
            )
        if not certification_number:
            raise ValueError(
                f"Row {row_number}: certified candidate requires certification_number"
            )
        if certification_expires_at is None:
            raise ValueError(
                f"Row {row_number}: certified candidate requires certification_expires_at"
            )

    return Candidate(
        name=name,
        place_type=place_type,
        address=empty_to_none(row.get("address")),
        district=empty_to_none(row.get("district")),
        province=empty_to_none(row.get("province")),
        phone=empty_to_none(row.get("phone")),
        latitude=latitude,
        longitude=longitude,
        proposed_trust_status=trust_status,
        source_type=source_type,
        source_reference=source_reference,
        external_provider=external_provider,
        external_id=external_id,
        certification_number=certification_number,
        certification_expires_at=certification_expires_at,
        review_state=review_state,
        review_note=empty_to_none(row.get("review_note")),
        review_hold_reason=empty_to_none(row.get("review_hold_reason")),
    )


def load_candidates(path: Path) -> list[Candidate]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [
            parse_candidate(row, row_number)
            for row_number, row in enumerate(csv.DictReader(handle), start=2)
        ]


UPSERT_CANDIDATE_SQL = text(
    """
    INSERT INTO place_candidates (
        name,
        place_type,
        address,
        district,
        province,
        phone,
        latitude,
        longitude,
        proposed_trust_status,
        source_type,
        source_reference,
        external_provider,
        external_id,
        certification_number,
        certification_expires_at,
        review_state,
        review_note,
        review_hold_reason,
        updated_at
    )
    VALUES (
        :name,
        CAST(:place_type AS place_type),
        :address,
        :district,
        :province,
        :phone,
        :latitude,
        :longitude,
        CAST(:proposed_trust_status AS trust_status),
        CAST(:source_type AS verification_source_type),
        :source_reference,
        :external_provider,
        :external_id,
        :certification_number,
        :certification_expires_at,
        CAST(:review_state AS candidate_review_state),
        :review_note,
        :review_hold_reason,
        now()
    )
    ON CONFLICT (external_provider, external_id)
      WHERE external_provider IS NOT NULL AND external_id IS NOT NULL
    DO UPDATE SET
        name = EXCLUDED.name,
        place_type = EXCLUDED.place_type,
        address = EXCLUDED.address,
        district = EXCLUDED.district,
        province = EXCLUDED.province,
        phone = EXCLUDED.phone,
        latitude = COALESCE(EXCLUDED.latitude, place_candidates.latitude),
        longitude = COALESCE(EXCLUDED.longitude, place_candidates.longitude),
        proposed_trust_status = EXCLUDED.proposed_trust_status,
        source_type = EXCLUDED.source_type,
        source_reference = EXCLUDED.source_reference,
        certification_number = EXCLUDED.certification_number,
        certification_expires_at = EXCLUDED.certification_expires_at,
        review_state = CASE
            WHEN place_candidates.review_state IN ('APPROVED', 'PROMOTED', 'REJECTED')
                THEN place_candidates.review_state
            WHEN place_candidates.review_state = 'GEOCODED'
                 AND EXCLUDED.review_state = 'DISCOVERED'
                THEN place_candidates.review_state
            ELSE EXCLUDED.review_state
        END,
        review_note = CASE
            WHEN place_candidates.review_state = 'DISCOVERED'
                THEN COALESCE(EXCLUDED.review_note, place_candidates.review_note)
            ELSE place_candidates.review_note
        END,
        review_hold_reason = CASE
            WHEN place_candidates.review_state = 'DISCOVERED'
                THEN COALESCE(
                    EXCLUDED.review_hold_reason,
                    place_candidates.review_hold_reason
                )
            ELSE place_candidates.review_hold_reason
        END,
        updated_at = now()
    """
)


async def apply_candidates(candidates: list[Candidate]) -> None:
    async with SessionLocal() as session, session.begin():
        for candidate in candidates:
            await session.execute(
                UPSERT_CANDIDATE_SQL,
                {
                    "name": candidate.name,
                    "place_type": candidate.place_type,
                    "address": candidate.address,
                    "district": candidate.district,
                    "province": candidate.province,
                    "phone": candidate.phone,
                    "latitude": candidate.latitude,
                    "longitude": candidate.longitude,
                    "proposed_trust_status": candidate.proposed_trust_status,
                    "source_type": candidate.source_type,
                    "source_reference": candidate.source_reference,
                    "external_provider": candidate.external_provider,
                    "external_id": candidate.external_id,
                    "certification_number": candidate.certification_number,
                    "certification_expires_at": candidate.certification_expires_at,
                    "review_state": candidate.review_state,
                    "review_note": candidate.review_note,
                    "review_hold_reason": candidate.review_hold_reason,
                },
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and optionally stage discovered place candidates."
    )
    parser.add_argument("csv_path", type=Path)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write candidates to place_candidates. Default is dry-run.",
    )
    return parser


async def async_main() -> int:
    args = build_parser().parse_args()
    candidates = load_candidates(args.csv_path)

    print(f"Validated candidate records: {len(candidates)}")
    for candidate in candidates:
        print(
            f"- {candidate.name}: {candidate.place_type} "
            f"[{candidate.proposed_trust_status}] {candidate.review_state}"
        )

    if not args.apply:
        print("Dry run only. Re-run with --apply to write candidate staging data.")
        return 0

    await apply_candidates(candidates)
    print(f"Staged {len(candidates)} candidates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))
