from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _normalize_profile_update_payload(data: Any) -> Any:
    """Map all-lowercase keys to camelCase aliases.

    Some proxies or clients send JSON with lowercased keys (``heightm``). Pydantic
    aliases are case-sensitive, so ``heightM`` would not match and numeric fields
    would stay unset while plain names like ``birthday`` still parse.
    """
    if not isinstance(data, dict):
        return data
    key_map = {
        "heightm": "heightM",
        "weightkg": "weightKg",
        "dailycaloriestarget": "dailyCaloriesTarget",
        "weightgoalkg": "weightGoalKg",
    }
    out: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(key, str):
            out[key_map.get(key.lower(), key)] = value
        else:
            out[key] = value
    return out


class ProfileRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    height_m: float | None = Field(None, alias="heightM")
    weight_kg: float | None = Field(None, alias="weightKg")
    daily_calories_target: int | None = Field(None, alias="dailyCaloriesTarget")
    weight_goal_kg: float | None = Field(None, alias="weightGoalKg")
    birthday: date | None = None
    gender: str | None = None


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _normalize_keys(cls, data: Any) -> Any:
        return _normalize_profile_update_payload(data)

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
