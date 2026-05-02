from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Create user (Swagger / admin only — not exposed in the PWA)."""

    email: EmailStr
    display_name: str = Field(..., min_length=1, max_length=255)
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=6, max_length=256)


class UserCreateResponse(BaseModel):
    id: str
    email: str
    display_name: str
    username: str
