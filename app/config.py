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
