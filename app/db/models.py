from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    profile: Mapped["UserProfile | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    weight_entries: Mapped[list["WeightEntry"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    food_options: Mapped[list["FoodOption"]] = relationship(back_populates="user")
    food_log_entries: Mapped[list["FoodLogEntry"]] = relationship(back_populates="user")
    exercise_entries: Mapped[list["ExerciseEntry"]] = relationship(back_populates="user")
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class PasswordResetToken(Base):
    """One-time token for POST /api/auth/reset-password (email link)."""

    __tablename__ = "password_reset_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    user: Mapped["User"] = relationship(back_populates="password_reset_tokens")


class UserProfile(Base):
    """One row per user; mirrors habit_tracker_frontend UserProfile (localStorage)."""

    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    height_m: Mapped[float | None] = mapped_column(Numeric(5, 3), nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    daily_calories_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_goal_kg: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    gender: Mapped[str | None] = mapped_column(
        SqlEnum("male", "female", name="user_profile_gender", native_enum=True), nullable=True
    )
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="profile")


class WeightEntry(Base):
    """Weight history; mirrors habit_tracker_frontend WeightHistoryEntry."""

    __tablename__ = "weight_entries"
    __table_args__ = (UniqueConstraint("user_id", "logged_date", name="uq_weight_user_date"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    logged_date: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="weight_entries")


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
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
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
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
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
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="exercise_entries")
