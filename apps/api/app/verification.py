from datetime import datetime, timezone

CERTIFIED_STATUSES = {"HALAL_CERTIFIED", "HALAL_CERTIFIED_SERVICE"}


def certification_is_current(
    trust_status: str,
    expires_at: datetime | None,
    *,
    now: datetime | None = None,
) -> bool:
    if trust_status not in CERTIFIED_STATUSES:
        return True

    if expires_at is None:
        return False

    current = now or datetime.now(timezone.utc)
    expiry = expires_at
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    return expiry > current
