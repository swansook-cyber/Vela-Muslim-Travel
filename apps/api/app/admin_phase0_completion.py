from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .admin_queries import list_admin_audit, list_candidates
from .admin_review_progress import load_candidate_review_progress
from .admin_schemas import CandidateReviewState
from .tools.pilot_readiness import load_readiness, readiness_passes


async def load_phase0_completion(session: AsyncSession) -> dict:
    candidates = await list_candidates(
        session,
        review_state=None,
        pilot_only=True,
        limit=500,
    )
    review_progress = await load_candidate_review_progress(session)
    production = await load_readiness()

    state_counts = {
        state.value: sum(1 for row in candidates if row["review_state"] == state.value)
        for state in CandidateReviewState
    }
    approved_waiting_promotion = state_counts[CandidateReviewState.APPROVED.value]
    active_review_pending = review_progress["pending"]
    production_ready = readiness_passes(production)

    audit = await list_admin_audit(session, limit=100)
    acceptance = next(
        (item for item in audit if item["action"] == "PHASE0_ACCEPTANCE"),
        None,
    )
    latest_candidate_update = max(
        (row["updated_at"] for row in candidates),
        default=None,
    )
    acceptance_current = bool(
        acceptance
        and (
            latest_candidate_update is None
            or acceptance["created_at"] >= latest_candidate_update
        )
    )

    blockers: list[str] = []
    if active_review_pending:
        blockers.append(
            f"{active_review_pending} pilot candidates still need coordinate/evidence review"
        )
    if approved_waiting_promotion:
        blockers.append(
            f"{approved_waiting_promotion} approved pilot candidates still need promotion"
        )
    if not production_ready:
        blockers.append(
            "production coverage gate is not complete for the seven-province pilot"
        )

    mechanical_ready = not blockers
    final_complete = mechanical_ready and acceptance_current

    return {
        "mechanical_ready": mechanical_ready,
        "final_complete": final_complete,
        "candidate_review_complete": active_review_pending == 0,
        "promotion_queue_complete": approved_waiting_promotion == 0,
        "production_coverage_ready": production_ready,
        "active_review_pending": active_review_pending,
        "approved_waiting_promotion": approved_waiting_promotion,
        "promoted_candidates": state_counts[CandidateReviewState.PROMOTED.value],
        "rejected_candidates": state_counts[CandidateReviewState.REJECTED.value],
        "manual_hold": review_progress["manual_hold"],
        "google_fast_lane": review_progress["google_fast_lane"],
        "blockers": blockers,
        "manual_acceptance_required": not final_complete,
        "accepted_at": (
            acceptance["created_at"] if acceptance_current and acceptance else None
        ),
        "manual_acceptance_steps": [
            "Run the real pilot route smoke matrix at 2/5/10 km.",
            "Require the 5 km route to include restaurant, prayer, and accommodation coverage.",
            "Inspect returned places for sensible real-world detours and evidence freshness.",
            "Record the final manual Phase 0 acceptance result.",
        ],
    }
