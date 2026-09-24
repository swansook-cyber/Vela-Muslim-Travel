import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status

from .config import get_settings

AdminKeyHeader = Annotated[str | None, Header(alias="X-Admin-Key")]


async def require_admin(x_admin_key: AdminKeyHeader = None) -> None:
    expected = get_settings().admin_api_key

    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API is disabled",
        )

    if x_admin_key is None or not secrets.compare_digest(x_admin_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key",
        )
