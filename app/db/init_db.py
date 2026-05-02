"""Create all tables from SQLAlchemy models (requires DATABASE_URL)."""

import os
from pathlib import Path
from urllib.parse import quote_plus

from app.config import get_database_url
from app.db.base import Base
from app.db.session import get_engine


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_dotenv_file() -> None:
    """Load `.env` from the backend package root (same folder as `pyproject.toml`)."""
    env_path = _backend_root() / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        if key:
            os.environ[key] = value


def _coerce_database_url() -> None:
    """Railway / CLI helpers: accept `mysql://` or discrete MYSQL* vars."""
    raw = (os.getenv("DATABASE_URL") or "").strip()
    if raw.startswith("mysql://") and not raw.startswith("mysql+pymysql://"):
        rest = raw.removeprefix("mysql://")
        merged = f"mysql+pymysql://{rest}"
        if "charset=" not in merged:
            merged += "&charset=utf8mb4" if "?" in merged else "?charset=utf8mb4"
        os.environ["DATABASE_URL"] = merged
        return

    if get_database_url():
        return

    host = os.getenv("MYSQLHOST") or os.getenv("MYSQL_HOST")
    port = os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT") or "3306"
    user = os.getenv("MYSQLUSER") or os.getenv("MYSQL_USER")
    password = os.getenv("MYSQLPASSWORD") or os.getenv("MYSQL_PASSWORD") or ""
    database = os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DATABASE") or "railway"
    if host and user:
        u = quote_plus(user, safe="")
        p = quote_plus(password, safe="")
        d = quote_plus(database, safe="")
        os.environ["DATABASE_URL"] = (
            f"mysql+pymysql://{u}:{p}@{host}:{port}/{d}?charset=utf8mb4"
        )


def init_db() -> None:
    if not get_database_url():
        env_hint = _backend_root() / ".env"
        raise SystemExit(
            "No DATABASE_URL found.\n\n"
            "Railway's default database name is often `railway` — that only names the DB; "
            "you still need a full connection string (or MYSQL* variables).\n\n"
            f"Create `{env_hint}` with either:\n"
            "  DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:PORT/railway?charset=utf8mb4\n"
            "or paste Railway’s `mysql://...` URL as DATABASE_URL=mysql://... (it will be converted).\n\n"
            "Alternatively export Railway’s discrete vars, then run again:\n"
            "  MYSQLHOST MYSQLPORT MYSQLUSER MYSQLPASSWORD MYSQLDATABASE\n"
        )
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    _load_dotenv_file()
    _coerce_database_url()
    init_db()
    print("Tables created (or already present).")
