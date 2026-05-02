"""FastAPI dependencies: DB session, shared APP_TOKEN bearer, profile user for /me."""

from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db


def _app_token_expected() -> str:
    return os.getenv("APP_TOKEN", "").strip()


def verify_app_bearer(authorization: str | None = Header(None)) -> None:
    """When ``APP_TOKEN`` is set, ``Authorization: Bearer`` must match it exactly."""
    expected = _app_token_expected()
    if not expected:
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization: Bearer (same value as server APP_TOKEN)",
        )
    token = authorization[7:].strip()
    if token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def _resolve_me_user(db: Session) -> User:
    """Which row ``/api/me`` uses: ``APP_USER_ID`` or the only user in the database."""
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
        detail="Multiple users exist — set APP_USER_ID on the server to choose which account /api/me uses",
    )


def get_me_user(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> User:
    verify_app_bearer(authorization)
    return _resolve_me_user(db)


DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_me_user)]
