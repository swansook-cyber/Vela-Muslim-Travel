from collections import Counter
from pathlib import Path

from app.tools.candidate_queue_readiness import (
    PILOT_PROVINCES,
    candidate_queue_passes,
    load_candidate_counts,
)


def test_real_candidate_queue_has_route_food_and_prayer_coverage() -> None:
    path = Path("../../database/seeds/pilot_candidates_review_queue.csv")
    counts = load_candidate_counts(path)

    for province in PILOT_PROVINCES:
        assert counts[province]["RESTAURANT"] >= 1
        assert counts[province]["MOSQUE"] >= 1

    accommodation_provinces = [
        province
        for province in PILOT_PROVINCES
        if counts[province]["ACCOMMODATION"] >= 1
    ]
    assert len(accommodation_provinces) >= 2
    assert candidate_queue_passes(counts)


def test_candidate_queue_gate_fails_when_corridor_food_is_missing() -> None:
    counts = {
        province: Counter(
            {
                "RESTAURANT": 1,
                "MOSQUE": 1,
                "ACCOMMODATION": 1 if province in PILOT_PROVINCES[:2] else 0,
            }
        )
        for province in PILOT_PROVINCES
    }
    counts["ชุมพร"]["RESTAURANT"] = 0

    assert not candidate_queue_passes(counts)


def test_candidate_queue_gate_requires_accommodation_in_two_provinces() -> None:
    counts = {
        province: Counter({"RESTAURANT": 1, "MOSQUE": 1})
        for province in PILOT_PROVINCES
    }
    counts["นครศรีธรรมราช"]["ACCOMMODATION"] = 1

    assert not candidate_queue_passes(counts)
