"""Password hashing (bcrypt) and JWT access tokens."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

JWT_ALG = "HS256"


def _jwt_secret() -> str:
    return os.getenv("JWT_SECRET", "change-me-in-production").strip()


def _jwt_expires_days() -> int:
    raw = os.getenv("JWT_EXPIRES_DAYS", "30").strip()
    try:
        return max(1, min(int(raw), 365))
    except ValueError:
        return 30


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_password(plain: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("ascii"))
    except ValueError:
        return False


def create_access_token(*, user_id: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(days=_jwt_expires_days())
    payload: dict[str, Any] = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALG)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALG])
