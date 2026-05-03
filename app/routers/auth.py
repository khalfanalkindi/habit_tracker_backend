from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.config import get_session_max_age_seconds
from app.db.models import User
from app.deps import DbSession, verify_app_bearer
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    UserPublic,
)
from app.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(verify_app_bearer)])


def _find_user_by_identifier(db: Session, ident: str) -> User | None:
    ident = ident.strip()
    stmt = select(User).where(
        or_(User.email == ident, User.username == ident, User.display_name == ident),
    )
    return db.execute(stmt).scalar_one_or_none()


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: DbSession) -> LoginResponse:
    user = _find_user_by_identifier(db, body.identifier)
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    max_age = get_session_max_age_seconds()
    session_expires_at = datetime.now(timezone.utc) + timedelta(seconds=max_age)
    return LoginResponse(
        user=UserPublic(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            username=user.username,
        ),
        session_expires_at=session_expires_at,
    )


@router.post("/change-password", response_model=MessageResponse)
def change_password(body: ChangePasswordRequest, db: DbSession) -> MessageResponse:
    """Change password while you know the current one (used from the app when logged in)."""
    user = _find_user_by_identifier(db, body.identifier)
    if user is None or not verify_password(body.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    user.password_hash = hash_password(body.new_password)
    db.add(user)
    db.flush()
    return MessageResponse(message="Password updated.")
