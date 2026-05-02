"""Create all tables from SQLAlchemy models (requires DATABASE_URL or MYSQL* env)."""

import os
from pathlib import Path

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


def _sync_database_url_env() -> None:
    """If URL was inferred from MYSQL* vars, expose it on DATABASE_URL for other tools."""
    resolved = get_database_url()
    if resolved and not (os.getenv("DATABASE_URL") or "").strip():
        os.environ["DATABASE_URL"] = resolved


def init_db() -> None:
    if not get_database_url():
        env_hint = _backend_root() / ".env"
        raise SystemExit(
            "No database connection configured.\n\n"
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
    _sync_database_url_env()
    init_db()
    print("Tables created (or already present).")
