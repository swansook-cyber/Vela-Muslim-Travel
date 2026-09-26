from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from .admin_queries import list_candidates
from .admin_schemas import CandidateReviewState
from .candidate_review import candidate_approval_blockers
from .tools.candidate_queue_readiness import PILOT_PROVINCES


async def load_candidate_review_progress(session: AsyncSession) -> dict:
    rows = await list_candidates(session, review_state=None, limit=500)
    active_states = {
        CandidateReviewState.DISCOVERED.value,
        CandidateReviewState.GEOCODED.value,
    }

    per_province: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "pending": 0,
            "ready_to_approve": 0,
            "blocked": 0,
            "coordinate_pending": 0,
            "google_resolvable": 0,
            "manual_hold": 0,
            "evidence_blocked": 0,
        }
    )

    pending = 0
    ready_to_approve = 0
    blocked = 0
    coordinate_pending = 0
    google_resolvable = 0
    manual_hold = 0
    evidence_blocked = 0

    for row in rows:
        if row["review_state"] not in active_states:
            continue
        if row.get("province") not in PILOT_PROVINCES:
            continue

        blockers = candidate_approval_blockers(row)
        province = row["province"]
        has_coordinate_gap = (
            row.get("latitude") is None
            or row.get("longitude") is None
            or row.get("coordinate_checked_at") is None
        )
        has_manual_hold = bool(row.get("review_hold_reason"))
        is_google_resolvable = (
            has_coordinate_gap
            and row.get("review_state") == CandidateReviewState.DISCOVERED.value
            and row.get("external_provider") in {"google_business", "google_places"}
            and bool(row.get("external_id"))
        )
        non_coordinate_or_hold_blockers = [
            blocker
            for blocker in blockers
            if blocker not in {
                "reviewed coordinates are required",
                "coordinate verification date is required",
            }
            and not blocker.startswith("manual review hold:")
        ]

        pending += 1
        per_province[province]["pending"] += 1

        if has_coordinate_gap:
            coordinate_pending += 1
            per_province[province]["coordinate_pending"] += 1
        if is_google_resolvable:
            google_resolvable += 1
            per_province[province]["google_resolvable"] += 1
        if has_manual_hold:
            manual_hold += 1
            per_province[province]["manual_hold"] += 1
        if non_coordinate_or_hold_blockers:
            evidence_blocked += 1
            per_province[province]["evidence_blocked"] += 1

        if blockers:
            blocked += 1
            per_province[province]["blocked"] += 1
        else:
            ready_to_approve += 1
            per_province[province]["ready_to_approve"] += 1

    return {
        "pending": pending,
        "ready_to_approve": ready_to_approve,
        "blocked": blocked,
        "coordinate_pending": coordinate_pending,
        "google_resolvable": google_resolvable,
        "manual_hold": manual_hold,
        "evidence_blocked": evidence_blocked,
        "provinces": [
            {
                "province": province,
                **per_province[province],
            }
            for province in PILOT_PROVINCES
        ],
    }
