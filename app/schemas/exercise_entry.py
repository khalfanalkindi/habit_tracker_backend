"""Exercise entry schemas — JSON names match habit_tracker_frontend ``ExerciseEntry``."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

# habit_tracker_frontend EXERCISE_TYPES ids
ALLOWED_EXERCISE_TYPES = frozenset({"gym", "walk", "cardio", "swim", "yoga", "cycling"})


def _exercise_type_ok(v: str) -> str:
    s = v.strip()
    if s not in ALLOWED_EXERCISE_TYPES:
        raise ValueError(f"exerciseType must be one of: {', '.join(sorted(ALLOWED_EXERCISE_TYPES))}")
    return s


class ExerciseEntryRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    day_of_week: int = Field(serialization_alias="dayOfWeek")
    exercise_type: str = Field(serialization_alias="exerciseType")
    duration_minutes: int | None = Field(serialization_alias="duration")
    completed: bool
    completed_on_date: date | None = Field(serialization_alias="date")


class ExerciseEntryCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    day_of_week: int = Field(ge=0, le=6, alias="dayOfWeek")
    exercise_type: str = Field(min_length=1, max_length=32, alias="exerciseType")
    duration_minutes: int | None = Field(default=None, ge=1, alias="duration")
    completed: bool = False
    completed_on_date: date | None = Field(default=None, alias="date")

    @field_validator("exercise_type")
    @classmethod
    def exercise_type_allowed(cls, v: str) -> str:
        return _exercise_type_ok(v)


class ExerciseEntryUpdate(BaseModel):
    """Partial update (PATCH). Omitted fields unchanged; explicit nulls skipped in router."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    day_of_week: int | None = Field(default=None, ge=0, le=6, alias="dayOfWeek")
    exercise_type: str | None = Field(default=None, min_length=1, max_length=32, alias="exerciseType")
    duration_minutes: int | None = Field(default=None, ge=1, alias="duration")
    completed: bool | None = None
    completed_on_date: date | None = Field(default=None, alias="date")

    @field_validator("exercise_type")
    @classmethod
    def exercise_type_allowed(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return _exercise_type_ok(v)
