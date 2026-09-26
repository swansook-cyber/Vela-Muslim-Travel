import pytest

from app import main
from app.admin_schemas import Phase0AcceptanceRequest


@pytest.mark.asyncio
async def test_phase0_acceptance_requires_mechanical_ready(monkeypatch) -> None:
    async def fake_completion(session):
        return {"mechanical_ready": False}

    monkeypatch.setattr(main, "load_phase0_completion", fake_completion)

    with pytest.raises(main.HTTPException) as exc_info:
        await main.admin_phase0_acceptance(
            request=Phase0AcceptanceRequest(
                route_smoke_2km_checked=True,
                route_smoke_5km_core_pass=True,
                route_smoke_10km_checked=True,
                detours_and_evidence_checked=True,
            ),
            session=None,
            _admin=None,
        )

    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_phase0_acceptance_requires_all_manual_checks(monkeypatch) -> None:
    async def fake_completion(session):
        return {"mechanical_ready": True}

    monkeypatch.setattr(main, "load_phase0_completion", fake_completion)

    with pytest.raises(main.HTTPException) as exc_info:
        await main.admin_phase0_acceptance(
            request=Phase0AcceptanceRequest(
                route_smoke_2km_checked=True,
                route_smoke_5km_core_pass=False,
                route_smoke_10km_checked=True,
                detours_and_evidence_checked=True,
            ),
            session=None,
            _admin=None,
        )

    assert exc_info.value.status_code == 422
    assert "route_smoke_5km_core_pass" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_phase0_acceptance_logs_and_returns_refreshed_completion(
    monkeypatch,
) -> None:
    calls = {"completion": 0, "logged": None, "committed": False}

    async def fake_completion(session):
        calls["completion"] += 1
        if calls["completion"] == 1:
            return {"mechanical_ready": True}
        return {
            "mechanical_ready": True,
            "final_complete": True,
            "candidate_review_complete": True,
            "promotion_queue_complete": True,
            "production_coverage_ready": True,
            "active_review_pending": 0,
            "approved_waiting_promotion": 0,
            "promoted_candidates": 20,
            "rejected_candidates": 3,
            "manual_hold": 0,
            "google_fast_lane": 0,
            "blockers": [],
            "manual_acceptance_required": False,
            "accepted_at": None,
            "manual_acceptance_steps": [],
        }

    async def fake_log(
        session,
        *,
        action,
        entity_type,
        entity_id,
        details,
    ):
        calls["logged"] = {
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details,
        }

    class Session:
        async def commit(self):
            calls["committed"] = True

    monkeypatch.setattr(main, "load_phase0_completion", fake_completion)
    monkeypatch.setattr(main, "log_admin_action", fake_log)

    result = await main.admin_phase0_acceptance(
        request=Phase0AcceptanceRequest(
            route_smoke_2km_checked=True,
            route_smoke_5km_core_pass=True,
            route_smoke_10km_checked=True,
            detours_and_evidence_checked=True,
            note="route smoke accepted",
        ),
        session=Session(),
        _admin=None,
    )

    assert calls["committed"] is True
    assert calls["logged"]["action"] == "PHASE0_ACCEPTANCE"
    assert calls["logged"]["entity_type"] == "phase0"
    assert calls["logged"]["entity_id"] == "pilot"
    assert calls["logged"]["details"]["route_smoke_5km_core_pass"] is True
    assert result.final_complete is True
