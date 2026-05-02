"""Application configuration from environment variables."""

import os


def get_database_url() -> str | None:
    """MySQL URL, e.g. mysql+pymysql://user:pass@127.0.0.1:3306/habit_tracker?charset=utf8mb4"""
    url = os.getenv("DATABASE_URL", "").strip()
    return url or None
