"""Weight entry schemas — JSON matches habit_tracker_frontend ``WeightHistoryEntry`` (``date``, ``weightKg``)."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WeightEntryRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    logged_date: date = Field(serialization_alias="date")
    weight_kg: float = Field(serialization_alias="weightKg")


class WeightEntryCreate(BaseModel):
    """One row per user per calendar day (unique). POST replaces weight for that day if a row exists."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    logged_date: date = Field(alias="date")
    weight_kg: float = Field(alias="weightKg", gt=0, le=500)

    @field_validator("weight_kg")
    @classmethod
    def weight_finite(cls, v: float) -> float:
        if not float(v) == float(v):
            raise ValueError("weightKg must be a finite number")
        return float(v)


class WeightEntryUpdate(BaseModel):
    """Partial update. ``date`` / ``weightKg`` may be set independently."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    logged_date: date | None = Field(default=None, alias="date")
    weight_kg: float | None = Field(default=None, alias="weightKg", gt=0, le=500)

    @field_validator("weight_kg")
    @classmethod
    def weight_finite(cls, v: float | None) -> float | None:
        if v is None:
            return None
        if not float(v) == float(v):
            raise ValueError("weightKg must be a finite number")
        return float(v)
