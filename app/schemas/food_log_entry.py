"""Food log entry schemas — JSON names match habit_tracker_frontend ``FoodLogEntry`` + daily ``date``."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

# habit_tracker_frontend MEAL_TYPES ids
ALLOWED_MEAL_TYPES = frozenset({"breakfast", "lunch", "dinner", "snacks"})


def _meal_ok(v: str) -> str:
    s = v.strip()
    if s not in ALLOWED_MEAL_TYPES:
        raise ValueError(f"mealType must be one of: {', '.join(sorted(ALLOWED_MEAL_TYPES))}")
    return s


class FoodLogEntryRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    log_date: date = Field(serialization_alias="logDate")
    food_option_id: str = Field(serialization_alias="foodOptionId")
    meal_type: str = Field(serialization_alias="mealType")
    quantity: float


class FoodLogEntryCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    log_date: date = Field(alias="logDate")
    food_option_id: str = Field(min_length=1, max_length=36, alias="foodOptionId")
    meal_type: str = Field(min_length=1, max_length=32, alias="mealType")
    quantity: float = Field(gt=0)

    @field_validator("food_option_id")
    @classmethod
    def food_option_id_strip(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("foodOptionId must not be empty")
        return s

    @field_validator("meal_type")
    @classmethod
    def meal_type_ok(cls, v: str) -> str:
        return _meal_ok(v)


class FoodLogEntryUpdate(BaseModel):
    """Partial update (PATCH). Omitted fields are unchanged."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    log_date: date | None = Field(default=None, alias="logDate")
    food_option_id: str | None = Field(default=None, min_length=1, max_length=36, alias="foodOptionId")
    meal_type: str | None = Field(default=None, min_length=1, max_length=32, alias="mealType")
    quantity: float | None = Field(default=None, gt=0)

    @field_validator("food_option_id")
    @classmethod
    def food_option_id_strip(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            raise ValueError("foodOptionId must not be empty")
        return s

    @field_validator("meal_type")
    @classmethod
    def meal_type_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return _meal_ok(v)
