from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """Login with email, username, or display_name (unique fields)."""

    identifier: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=256)


class UserPublic(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True, populate_by_name=True)

    id: str
    email: str
    display_name: str = Field(serialization_alias="displayName")
    username: str


class LoginResponse(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    user: UserPublic
    session_expires_at: datetime = Field(
        serialization_alias="sessionExpiresAt",
        description="Client should treat the session as invalid after this instant.",
    )


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    identifier: str = Field(..., min_length=1, max_length=255)
    old_password: str = Field(..., min_length=1, max_length=256, alias="oldPassword")
    new_password: str = Field(..., min_length=8, max_length=256, alias="newPassword")


class ForgotPasswordRequest(BaseModel):
    identifier: str = Field(..., min_length=1, max_length=255)


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    token: str = Field(..., min_length=10, max_length=256)
    new_password: str = Field(..., min_length=8, max_length=256, alias="newPassword")


class MessageResponse(BaseModel):
    message: str


class ForgotPasswordResponse(BaseModel):
    model_config = ConfigDict(serialize_by_alias=True)

    message: str
    reset_link: str | None = Field(
        default=None,
        serialization_alias="resetLink",
        description="Only set when PASSWORD_RESET_RETURN_LINK_IN_RESPONSE=true (local dev).",
    )
