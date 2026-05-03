"""Application configuration from environment variables."""

from __future__ import annotations

import os
from urllib.parse import quote_plus


def get_database_url() -> str | None:
    """Resolve MySQL URL for SQLAlchemy (pymysql driver).

    Resolution order:
    1. ``DATABASE_URL`` if set (``mysql://`` from Railway is upgraded to ``mysql+pymysql://``).
    2. Else build from Railway / Docker style ``MYSQLHOST``, ``MYSQLUSER``, ``MYSQLPASSWORD``,
       ``MYSQLPORT``, ``MYSQLDATABASE`` (or ``MYSQL_*`` spellings) when host + user exist.
    """
    raw = (os.getenv("DATABASE_URL") or "").strip()

    if raw.startswith("mysql://") and not raw.startswith("mysql+pymysql://"):
        rest = raw.removeprefix("mysql://")
        merged = f"mysql+pymysql://{rest}"
        if "charset=" not in merged:
            merged += "&charset=utf8mb4" if "?" in merged else "?charset=utf8mb4"
        return merged

    if raw:
        return raw

    host = os.getenv("MYSQLHOST") or os.getenv("MYSQL_HOST")
    port = os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT") or "3306"
    user = os.getenv("MYSQLUSER") or os.getenv("MYSQL_USER")
    password = os.getenv("MYSQLPASSWORD") or os.getenv("MYSQL_PASSWORD") or ""
    database = os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DATABASE") or "railway"
    if host and user:
        u = quote_plus(user, safe="")
        p = quote_plus(password, safe="")
        d = quote_plus(database, safe="")
        return f"mysql+pymysql://{u}:{p}@{host}:{port}/{d}?charset=utf8mb4"

    return None


def get_session_max_age_seconds() -> int:
    """Client session hint returned on login (browser enforces via localStorage)."""
    raw = (os.getenv("SESSION_MAX_AGE_SECONDS") or "").strip()
    if raw.isdigit() and int(raw) > 0:
        return int(raw)
    return 14 * 24 * 3600


def get_password_reset_ttl_hours() -> int:
    raw = (os.getenv("PASSWORD_RESET_TTL_HOURS") or "").strip()
    if raw.isdigit() and int(raw) > 0:
        return int(raw)
    return 1


def get_frontend_password_reset_base_url() -> str:
    """Origin + path prefix for reset links in emails (no trailing slash)."""
    return (os.getenv("FRONTEND_PASSWORD_RESET_BASE_URL") or "").strip().rstrip("/")


def smtp_configured() -> bool:
    return bool((os.getenv("SMTP_HOST") or "").strip())
