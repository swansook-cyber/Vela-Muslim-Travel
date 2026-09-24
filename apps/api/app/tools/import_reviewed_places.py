from __future__ import annotations

import argparse
import asyncio
import csv
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import text

from app.db import SessionLocal

ALLOWED_PLACE_TYPES = {"RESTAURANT", "ACCOMMODATION", "MOSQUE", "PRAYER_ROOM"}
ALLOWED_TRUST_STATUSES = {
    "HALAL_CERTIFIED",
    "HALAL_CERTIFIED_SERVICE",
    "MUSLIM_OWNED",
    "MUSLIM_FRIENDLY",
    "UNVERIFIED",
}
ALLOWED_SOURCE_TYPES = {
    "OFFICIAL_CERTIFICATION",
    "BUSINESS_OWNER",
    "FIELD_CHECK",
    "COMMUNITY_REPORT",
    "PUBLIC_WEB_SOURCE",
    "UNKNOWN",
}
CERTIFIED_STATUSES = {"HALAL_CERTIFIED", "HALAL_CERTIFIED_SERVICE"}


@dataclass(slots=True)
class ReviewedPlace:
    slug: str
    name_th: str
    name_en: str | None
    place_type: str
    latitude: float
    longitude: float
    address: str | None
    district: str | None
    province: str | None
    postal_code: str | None
    phone: str | None
    website_url: str | None
    social_url: str | None
    trust_status: str
    source_type: str
    source_reference: str | None
    verified_at: str | None
    expires_at: str | None
    review_note: str | None


def empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def parse_row(row: dict[str, str], row_number: int) -> ReviewedPlace | None:
    if row.get("review_state", "").strip().upper() != "APPROVED":
        return None

    slug = row.get("slug", "").strip()
    name_th = row.get("name_th", "").strip()
    place_type = row.get("place_type", "").strip().upper()
    trust_status = row.get("trust_status", "").strip().upper()
    source_type = row.get("source_type", "").strip().upper()
    source_reference = empty_to_none(row.get("source_reference"))

    if not slug or not name_th:
        raise ValueError(f"Row {row_number}: slug and name_th are required")
    if place_type not in ALLOWED_PLACE_TYPES:
        raise ValueError(f"Row {row_number}: invalid place_type {place_type!r}")
    if trust_status not in ALLOWED_TRUST_STATUSES:
        raise ValueError(f"Row {row_number}: invalid trust_status {trust_status!r}")
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError(f"Row {row_number}: invalid source_type {source_type!r}")

    try:
        latitude = float(row["latitude"])
        longitude = float(row["longitude"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Row {row_number}: valid latitude/longitude are required") from exc

    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError(f"Row {row_number}: coordinates are out of range")

    if (
        trust_status in CERTIFIED_STATUSES
        and (source_type != "OFFICIAL_CERTIFICATION" or not source_reference)
    ):
        raise ValueError(
            f"Row {row_number}: certified status requires OFFICIAL_CERTIFICATION "
            "and source_reference"
        )

    if place_type == "ACCOMMODATION" and trust_status == "HALAL_CERTIFIED":
        raise ValueError(
            f"Row {row_number}: accommodation must use HALAL_CERTIFIED_SERVICE "
            "for a certified service claim"
        )

    if place_type == "RESTAURANT" and trust_status == "HALAL_CERTIFIED_SERVICE":
        raise ValueError(
            f"Row {row_number}: restaurant certification must use HALAL_CERTIFIED"
        )

    return ReviewedPlace(
        slug=slug,
        name_th=name_th,
        name_en=empty_to_none(row.get("name_en")),
        place_type=place_type,
        latitude=latitude,
        longitude=longitude,
        address=empty_to_none(row.get("address")),
        district=empty_to_none(row.get("district")),
        province=empty_to_none(row.get("province")),
        postal_code=empty_to_none(row.get("postal_code")),
        phone=empty_to_none(row.get("phone")),
        website_url=empty_to_none(row.get("website_url")),
        social_url=empty_to_none(row.get("social_url")),
        trust_status=trust_status,
        source_type=source_type,
        source_reference=source_reference,
        verified_at=empty_to_none(row.get("verified_at")),
        expires_at=empty_to_none(row.get("expires_at")),
        review_note=empty_to_none(row.get("review_note")),
    )


def load_reviewed_places(path: Path) -> list[ReviewedPlace]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        places: list[ReviewedPlace] = []
        for row_number, row in enumerate(reader, start=2):
            parsed = parse_row(row, row_number)
            if parsed is not None:
                places.append(parsed)
    return places


UPSERT_PLACE_SQL = text(
    """
    INSERT INTO places (
        slug,
        place_type,
        name_th,
        name_en,
        location,
        address,
        district,
        province,
        postal_code,
        phone,
        website_url,
        social_url,
        active,
        source_status,
        updated_at
    )
    VALUES (
        :slug,
        CAST(:place_type AS place_type),
        :name_th,
        :name_en,
        ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography,
        :address,
        :district,
        :province,
        :postal_code,
        :phone,
        :website_url,
        :social_url,
        true,
        'REVIEWED_IMPORT',
        now()
    )
    ON CONFLICT (slug) DO UPDATE SET
        place_type = EXCLUDED.place_type,
        name_th = EXCLUDED.name_th,
        name_en = EXCLUDED.name_en,
        location = EXCLUDED.location,
        address = EXCLUDED.address,
        district = EXCLUDED.district,
        province = EXCLUDED.province,
        postal_code = EXCLUDED.postal_code,
        phone = EXCLUDED.phone,
        website_url = EXCLUDED.website_url,
        social_url = EXCLUDED.social_url,
        active = true,
        source_status = 'REVIEWED_IMPORT',
        updated_at = now()
    RETURNING id
    """
)

INSERT_VERIFICATION_SQL = text(
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
        CAST(:verified_at AS timestamptz),
        CAST(:expires_at AS timestamptz),
        :note,
        'CONTROLLED_IMPORT'
    WHERE NOT EXISTS (
        SELECT 1
        FROM place_verifications existing
        WHERE existing.place_id = :place_id
          AND existing.claim_type = 'MUSLIM_TRAVEL_STATUS'
          AND existing.trust_status = CAST(:trust_status AS trust_status)
          AND existing.source_type = CAST(:source_type AS verification_source_type)
          AND existing.source_reference IS NOT DISTINCT FROM :source_reference
          AND existing.verified_at IS NOT DISTINCT FROM CAST(:verified_at AS timestamptz)
          AND existing.expires_at IS NOT DISTINCT FROM CAST(:expires_at AS timestamptz)
    )
    """
)


async def apply_places(places: list[ReviewedPlace]) -> None:
    async with SessionLocal() as session, session.begin():
        for place in places:
            values = {
                "slug": place.slug,
                "place_type": place.place_type,
                "name_th": place.name_th,
                "name_en": place.name_en,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "address": place.address,
                "district": place.district,
                "province": place.province,
                "postal_code": place.postal_code,
                "phone": place.phone,
                "website_url": place.website_url,
                "social_url": place.social_url,
            }
            result = await session.execute(UPSERT_PLACE_SQL, values)
            place_id = result.scalar_one()

            await session.execute(
                INSERT_VERIFICATION_SQL,
                {
                    "place_id": place_id,
                    "trust_status": place.trust_status,
                    "source_type": place.source_type,
                    "source_reference": place.source_reference,
                    "verified_at": place.verified_at,
                    "expires_at": place.expires_at,
                    "note": place.review_note,
                },
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and optionally import manually reviewed place records."
    )
    parser.add_argument("csv_path", type=Path)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write approved records to PostGIS. Without this flag the command is dry-run only.",
    )
    return parser


async def async_main() -> int:
    args = build_parser().parse_args()
    places = load_reviewed_places(args.csv_path)

    print(f"Validated approved records: {len(places)}")
    for place in places:
        print(
            f"- {place.slug}: {place.place_type} "
            f"{place.latitude:.6f},{place.longitude:.6f} [{place.trust_status}]"
        )

    if not args.apply:
        print("Dry run only. Re-run with --apply to write to the database.")
        return 0

    await apply_places(places)
    print(f"Imported {len(places)} approved records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(async_main()))
