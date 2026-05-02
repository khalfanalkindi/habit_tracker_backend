from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP(6)"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP(6)"),
        server_onupdate=text("CURRENT_TIMESTAMP(6)"),
        nullable=False,
    )

    food_options: Mapped[list[FoodOption]] = relationship(back_populates="user")
    food_log_entries: Mapped[list[FoodLogEntry]] = relationship(back_populates="user")
    exercise_entries: Mapped[list[ExerciseEntry]] = relationship(back_populates="user")


class FoodOption(Base):
    __tablename__ = "food_options"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    calories_per_serving: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    protein_g_per_serving: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    carbs_g_per_serving: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    fat_g_per_serving: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    serving_size: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    serving_unit: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP(6)"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP(6)"),
        server_onupdate=text("CURRENT_TIMESTAMP(6)"),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="food_options")
    log_entries: Mapped[list[FoodLogEntry]] = relationship(back_populates="food_option")


class FoodLogEntry(Base):
    __tablename__ = "food_log_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    food_option_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("food_options.id", ondelete="RESTRICT")
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    meal_type: Mapped[str] = mapped_column(String(32), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP(6)"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP(6)"),
        server_onupdate=text("CURRENT_TIMESTAMP(6)"),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="food_log_entries")
    food_option: Mapped[FoodOption] = relationship(back_populates="log_entries")


class ExerciseEntry(Base):
    __tablename__ = "exercise_entries"
    __table_args__ = (CheckConstraint("day_of_week BETWEEN 0 AND 6", name="chk_exercise_day_of_week"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    exercise_type: Mapped[str] = mapped_column(String(32), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("0")
    )
    completed_on_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP(6)"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP(6)"),
        server_onupdate=text("CURRENT_TIMESTAMP(6)"),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="exercise_entries")
