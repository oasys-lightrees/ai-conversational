"""Admin authentication — shared-key bearer check."""

from __future__ import annotations

from fastapi import Header, HTTPException, status

from backend.config import settings


def require_admin(authorization: str | None = Header(default=None)) -> None:
    """Gate an admin route on the shared ``ADMIN_API_KEY``.

    503 if the admin API is unconfigured (no key set); 401 on a missing or
    incorrect bearer token.
    """
    key = settings.admin_api_key
    if not key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API is not configured.",
        )
    if authorization != f"Bearer {key}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized.",
        )
