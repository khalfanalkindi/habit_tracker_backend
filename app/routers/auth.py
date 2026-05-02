from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select

from app.db.models import User
from app.deps import DbSession, verify_app_bearer
from app.schemas.auth import LoginRequest, LoginResponse, UserPublic
from app.security import verify_password

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(verify_app_bearer)])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: DbSession) -> LoginResponse:
    ident = body.identifier.strip()
    stmt = select(User).where(
        or_(User.email == ident, User.username == ident, User.display_name == ident)
    )
    user = db.execute(stmt).scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return LoginResponse(
        user=UserPublic(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            username=user.username,
        ),
    )
