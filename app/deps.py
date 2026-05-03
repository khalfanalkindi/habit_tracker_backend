"""FastAPI dependencies: DB session, shared APP_TOKEN bearer, /api/me user identity."""

from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db

_bearer = HTTPBearer(auto_error=False, scheme_name="BearerAuth")


def _app_token_expected() -> str:
    return os.getenv("APP_TOKEN", "").strip()


def verify_app_bearer(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> None:
    """When ``APP_TOKEN`` is set, require ``Authorization: Bearer`` matching it (OpenAPI: single Bearer scheme)."""
    expected = _app_token_expected()
    if not expected:
        return
    if credentials is None or (credentials.scheme or "").lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization: Bearer (same value as server APP_TOKEN)",
        )
    token = credentials.credentials.strip()
    if token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def _resolve_me_user_fallback(db: Session) -> User:
    """Pick user when no ``X-User-Id`` header: ``APP_USER_ID`` or the only row in ``users``."""
    uid = os.getenv("APP_USER_ID", "").strip()
    if uid:
        user = db.get(User, uid)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="APP_USER_ID does not match any user",
            )
        return user
    rows = list(db.scalars(select(User).order_by(User.created_at.asc())).all())
    if len(rows) == 1:
        return rows[0]
    if len(rows) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users in database yet",
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            "Several accounts exist — send header X-User-Id with the logged-in user's id "
            "(from POST /api/auth/login response), or set APP_USER_ID on the server."
        ),
    )


def get_me_user(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
    db: Session = Depends(get_db),
) -> User:
    """Resolve ``/api/me`` user. Prefer ``X-User-Id`` (client login) so CRUD targets the right row.

    Router must include ``Depends(verify_app_bearer)`` so the bearer token is checked first.
    """
    uid = (x_user_id or "").strip()
    if uid:
        user = db.get(User, uid)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="X-User-Id does not match any user",
            )
        return user
    return _resolve_me_user_fallback(db)


DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_me_user)]
