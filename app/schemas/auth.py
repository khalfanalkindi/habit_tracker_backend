from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login with email, username, or display_name (unique fields)."""

    identifier: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=256)


class UserPublic(BaseModel):
    id: str
    email: str
    display_name: str
    username: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
