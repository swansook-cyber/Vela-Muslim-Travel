from datetime import UTC, datetime, timedelta

import pytest

from app.admin_verifications import validate_verification_claim


def test_certified_admin_verification_requires_official_source() -> None:
    with pytest.raises(ValueError, match="official source"):
        validate_verification_claim(
            trust_status="HALAL_CERTIFIED",
            source_type="PUBLIC_WEB_SOURCE",
            source_reference="https://example.com",
            expires_at=datetime.now(UTC) + timedelta(days=30),
        )


def test_certified_admin_verification_requires_current_expiry() -> None:
    with pytest.raises(ValueError, match="current expiry"):
        validate_verification_claim(
            trust_status="HALAL_CERTIFIED",
            source_type="OFFICIAL_CERTIFICATION",
            source_reference="https://halal.example/cert",
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )


def test_non_certified_claim_allows_non_expiring_public_source() -> None:
    validate_verification_claim(
        trust_status="MUSLIM_FRIENDLY",
        source_type="PUBLIC_WEB_SOURCE",
        source_reference="https://example.com/listing",
        expires_at=None,
    )
