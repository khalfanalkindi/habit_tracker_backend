from __future__ import annotations

import hashlib
import logging
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.config import (
    get_frontend_password_reset_base_url,
    get_password_reset_ttl_hours,
    get_session_max_age_seconds,
    smtp_configured,
)
from app.db.models import PasswordResetToken, User
from app.deps import DbSession, verify_app_bearer
from app.mailer import send_password_reset_email
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    ResetPasswordRequest,
    UserPublic,
)
from app.security import hash_password, verify_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(verify_app_bearer)])


def _token_hash(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


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


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(body: ForgotPasswordRequest, db: DbSession) -> ForgotPasswordResponse:
    """Always responds 200 with the same shape to avoid account enumeration."""
    generic = ForgotPasswordResponse(
        message="If an account matches, check your email for a reset link when mail is configured.",
    )
    user = _find_user_by_identifier(db, body.identifier)
    if user is None:
        return generic

    db.execute(delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id))
    raw = secrets.token_urlsafe(32)
    ttl_h = get_password_reset_ttl_hours()
    expires_at = datetime.utcnow() + timedelta(hours=ttl_h)
    row = PasswordResetToken(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token_hash=_token_hash(raw),
        expires_at=expires_at,
        used_at=None,
    )
    db.add(row)
    db.flush()

    base = get_frontend_password_reset_base_url()
    path = "/reset-password"
    link = f"{base}{path}?token={raw}" if base else f"{path}?token={raw}"

    sent = False
    if smtp_configured():
        sent = send_password_reset_email(user.email, link)
        if not sent:
            logger.warning("Password reset token created for %s but SMTP delivery failed", user.email)

    dev_return = (os.getenv("PASSWORD_RESET_RETURN_LINK_IN_RESPONSE") or "").lower() in (
        "1",
        "true",
        "yes",
    )
    reset_link: str | None = None
    if dev_return:
        reset_link = link
        logger.warning("PASSWORD_RESET_RETURN_LINK_IN_RESPONSE is enabled — reset link exposed in JSON")

    return ForgotPasswordResponse(
        message=generic.message,
        reset_link=reset_link,
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(body: ResetPasswordRequest, db: DbSession) -> MessageResponse:
    h = _token_hash(body.token.strip())
    row = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash == h))
    now = datetime.utcnow()
    if row is None or row.used_at is not None or row.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    user = db.get(User, row.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    user.password_hash = hash_password(body.new_password)
    row.used_at = now
    db.add(user)
    db.add(row)
    db.flush()
    return MessageResponse(message="Password updated. You can sign in with the new password.")
