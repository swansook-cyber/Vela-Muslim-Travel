import pytest
from pydantic import ValidationError

from app.admin_schemas import AdminVerificationCreate


def test_admin_verification_rejects_unknown_trust_status() -> None:
    with pytest.raises(ValidationError):
        AdminVerificationCreate(
            trust_status="CERTIFIED_BY_REVIEW",
            source_type="PUBLIC_WEB_SOURCE",
            verified_at="2026-09-25T00:00:00+07:00",
        )


def test_admin_verification_rejects_unknown_source_type() -> None:
    with pytest.raises(ValidationError):
        AdminVerificationCreate(
            trust_status="UNVERIFIED",
            source_type="SOCIAL_MEDIA_GUESS",
            verified_at="2026-09-25T00:00:00+07:00",
        )
