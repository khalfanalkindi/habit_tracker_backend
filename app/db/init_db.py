"""Create all tables from SQLAlchemy models (requires DATABASE_URL)."""

from app.config import get_database_url
from app.db.base import Base
from app.db.session import get_engine


def init_db() -> None:
    if not get_database_url():
        raise SystemExit(
            "Set DATABASE_URL first, e.g.\n"
            "  export DATABASE_URL='mysql+pymysql://root:secret@127.0.0.1:3306/habit_tracker?charset=utf8mb4'\n"
            "Create the database if needed (see db/schema.sql), then run:\n"
            "  python -m app.db.init_db"
        )
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Tables created (or already present).")
