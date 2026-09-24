from datetime import UTC, datetime, timedelta

import pytest

from app.verification import certification_is_current


def validate_admin_verification(
    *,
    trust_status: str,
    source_type: str,
    source_reference: str | None,
    expires_at: datetime | None,
) -> None:
    if trust_status in {"HALAL_CERTIFIED", "HALAL_CERTIFIED_SERVICE"}:
        if source_type != "OFFICIAL_CERTIFICATION" or not source_reference:
            raise ValueError("Certified status requires official source evidence")
        if not certification_is_current(trust_status, expires_at):
            raise ValueError("Certified status requires a current expiry date")


def test_certified_admin_verification_requires_official_source() -> None:
    with pytest.raises(ValueError, match="official source"):
        validate_admin_verification(
            trust_status="HALAL_CERTIFIED",
            source_type="PUBLIC_WEB_SOURCE",
            source_reference="https://example.com",
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )


def test_certified_admin_verification_requires_current_expiry() -> None:
    with pytest.raises(ValueError, match="current expiry"):
        validate_admin_verification(
            trust_status="HALAL_CERTIFIED",
            source_type="OFFICIAL_CERTIFICATION",
            source_reference="https://halal.example/cert",
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
