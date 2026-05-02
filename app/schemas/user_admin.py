from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class UserListItem(BaseModel):
    """User row for admin list (no secrets)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    display_name: str
    username: str
    created_at: datetime
    updated_at: datetime
