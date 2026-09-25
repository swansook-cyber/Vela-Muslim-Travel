from app.admin_schemas import CandidateReviewState


def test_candidate_filter_enum_value() -> None:
    assert CandidateReviewState.DISCOVERED.value == "DISCOVERED"
