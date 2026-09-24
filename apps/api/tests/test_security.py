from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import app.security as security


@pytest.mark.asyncio
async def test_admin_api_is_disabled_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        security,
        "get_settings",
        lambda: SimpleNamespace(admin_api_key=None),
    )

    with pytest.raises(HTTPException) as exc_info:
        await security.require_admin(None)

    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_admin_api_rejects_wrong_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        security,
        "get_settings",
        lambda: SimpleNamespace(admin_api_key="expected-secret"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await security.require_admin("wrong-secret")

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_admin_api_accepts_matching_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        security,
        "get_settings",
        lambda: SimpleNamespace(admin_api_key="expected-secret"),
    )

    assert await security.require_admin("expected-secret") is None
