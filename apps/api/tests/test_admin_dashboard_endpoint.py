import pytest

from app import main


@pytest.mark.asyncio
async def test_admin_dashboard_reports_google_places_capability(monkeypatch) -> None:
    async def fake_get_admin_dashboard(session):
        return {
            "candidates_total": 24,
            "discovered": 8,
            "geocoded": 15,
            "approved": 0,
            "promoted": 0,
            "rejected": 0,
            "production_places": 4,
            "expired_verifications": 0,
            "certifications_expiring_30d": 1,
        }

    monkeypatch.setattr(main, "get_admin_dashboard", fake_get_admin_dashboard)
    monkeypatch.setattr(main.settings, "google_places_api_key", "configured")

    result = await main.admin_dashboard(session=None, _admin=None)

    assert result.google_places_resolver_enabled is True


@pytest.mark.asyncio
async def test_admin_dashboard_hides_unconfigured_google_places(monkeypatch) -> None:
    async def fake_get_admin_dashboard(session):
        return {
            "candidates_total": 24,
            "discovered": 8,
            "geocoded": 15,
            "approved": 0,
            "promoted": 0,
            "rejected": 0,
            "production_places": 4,
            "expired_verifications": 0,
            "certifications_expiring_30d": 1,
        }

    monkeypatch.setattr(main, "get_admin_dashboard", fake_get_admin_dashboard)
    monkeypatch.setattr(main.settings, "google_places_api_key", None)

    result = await main.admin_dashboard(session=None, _admin=None)

    assert result.google_places_resolver_enabled is False
