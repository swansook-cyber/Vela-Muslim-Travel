from __future__ import annotations

from urllib.parse import quote_plus

from .verification import certification_is_current

CERTIFIED_STATUSES = {"HALAL_CERTIFIED", "HALAL_CERTIFIED_SERVICE"}


def candidate_maps_search_url(candidate: dict) -> str:
    provider = candidate.get("external_provider")
    external_id = candidate.get("external_id")
    if provider in {"google_business", "google_places"} and external_id:
        return (
            "https://www.google.com/maps/search/?api=1"
            f"&query_place_id={quote_plus(str(external_id))}"
        )

    query = " ".join(
        str(value).strip()
        for value in (
            candidate.get("name"),
            candidate.get("address"),
            candidate.get("district"),
            candidate.get("province"),
        )
        if value
    )
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(query)


def candidate_approval_blockers(
    candidate: dict,
    *,
    latitude: float | None = None,
    longitude: float | None = None,
) -> list[str]:
    lat = candidate.get("latitude") if latitude is None else latitude
    lng = candidate.get("longitude") if longitude is None else longitude

    blockers: list[str] = []
    review_hold_reason = candidate.get("review_hold_reason")
    if review_hold_reason:
        blockers.append(f"manual review hold: {review_hold_reason}")

    if lat is None or lng is None:
        blockers.append("reviewed coordinates are required")
    elif candidate.get("coordinate_checked_at") is None:
        blockers.append("coordinate verification date is required")

    source_checked_at = candidate.get("source_checked_at")
    if source_checked_at is None:
        blockers.append("source cross-check date is required")

    source_type = candidate.get("source_type")
    source_reference = candidate.get("source_reference")
    if source_type != "UNKNOWN" and not source_reference:
        blockers.append("source reference is required")

    trust_status = candidate.get("proposed_trust_status")
    if trust_status in CERTIFIED_STATUSES:
        if source_type != "OFFICIAL_CERTIFICATION":
            blockers.append("certified status requires official certification source")
        if not candidate.get("certification_number"):
            blockers.append("certified status requires certificate number")
        if not certification_is_current(
            str(trust_status),
            candidate.get("certification_expires_at"),
        ):
            blockers.append("certified status requires current non-expired evidence")

    return blockers
