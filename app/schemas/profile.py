from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProfileRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    height_m: float | None = Field(None, alias="heightM")
    weight_kg: float | None = Field(None, alias="weightKg")
    daily_calories_target: int | None = Field(None, alias="dailyCaloriesTarget")
    weight_goal_kg: float | None = Field(None, alias="weightGoalKg")
    birthday: date | None = None
    gender: str | None = None


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    height_m: float | None = Field(None, alias="heightM")
    weight_kg: float | None = Field(None, alias="weightKg")
    daily_calories_target: int | None = Field(None, alias="dailyCaloriesTarget")
    weight_goal_kg: float | None = Field(None, alias="weightGoalKg")
    birthday: date | None = None
    gender: str | None = None

    @field_validator("gender")
    @classmethod
    def gender_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if v not in ("male", "female"):
            raise ValueError("gender must be 'male', 'female', or null")
        return v
