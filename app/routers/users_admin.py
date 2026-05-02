from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select

from app.db.models import User
from app.deps import DbSession, verify_app_bearer
from app.schemas.user_admin import UserCreate, UserCreateResponse, UserListItem
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["users-admin"], dependencies=[Depends(verify_app_bearer)])


@router.get("", response_model=list[UserListItem])
def list_users(db: DbSession) -> list[User]:
    """List all users (admin / Swagger)."""
    stmt = select(User).order_by(User.created_at.desc())
    return list(db.scalars(stmt).all())


@router.post("", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, db: DbSession) -> UserCreateResponse:
    """Create a user (intended for Swagger / ops only — not used by the PWA)."""
    email = str(body.email).strip().lower()
    username_norm = body.username.strip().lower()
    display = body.display_name.strip()
    stmt = select(User.id).where(
        or_(User.email == email, User.username == username_norm, User.display_name == display)
    )
    if db.scalars(stmt).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with same email, username, or display_name already exists",
        )
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        display_name=display,
        username=username_norm,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.flush()
    return UserCreateResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        username=user.username,
    )
