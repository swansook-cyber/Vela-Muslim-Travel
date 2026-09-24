from datetime import datetime, timedelta, timezone

from app.verification import certification_is_current


def test_non_certified_status_does_not_require_expiry() -> None:
    assert certification_is_current("UNVERIFIED", None)


def test_certified_status_requires_expiry() -> None:
    assert not certification_is_current("HALAL_CERTIFIED", None)


def test_expired_certification_is_not_current() -> None:
    now = datetime(2026, 9, 25, tzinfo=timezone.utc)
    assert not certification_is_current(
        "HALAL_CERTIFIED",
        now - timedelta(seconds=1),
        now=now,
    )


def test_future_certification_is_current() -> None:
    now = datetime(2026, 9, 25, tzinfo=timezone.utc)
    assert certification_is_current(
        "HALAL_CERTIFIED_SERVICE",
        now + timedelta(days=1),
        now=now,
    )
