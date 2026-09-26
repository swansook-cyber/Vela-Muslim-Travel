from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .admin_queries import list_candidates
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

    return {
        "mechanical_ready": mechanical_ready,
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
        "manual_acceptance_required": True,
        "manual_acceptance_steps": [
            "Run the real pilot route smoke matrix at 2/5/10 km.",
            "Require the 5 km route to include restaurant, prayer, and accommodation coverage.",
            "Inspect returned places for sensible real-world detours and evidence freshness.",
            "Record the final manual Phase 0 acceptance result.",
        ],
    }
