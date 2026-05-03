"""Food option schemas — JSON field names match habit_tracker_frontend ``FoodOption``."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FoodOptionRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    serving_size: float = Field(serialization_alias="servingSize")
    serving_unit: str = Field(serialization_alias="servingUnit", max_length=32)


class FoodOptionCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    name: str = Field(..., min_length=1, max_length=255)
    calories: float = Field(..., ge=0)
    protein: float = Field(..., ge=0)
    carbs: float = Field(..., ge=0)
    fat: float = Field(..., ge=0)
    serving_size: float = Field(..., gt=0, alias="servingSize")
    serving_unit: str = Field(..., min_length=1, max_length=32, alias="servingUnit")

    @field_validator("name")
    @classmethod
    def name_stripped(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("name must not be empty")
        return s

    @field_validator("serving_unit")
    @classmethod
    def unit_stripped(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("servingUnit must not be empty")
        return s


class FoodOptionUpdate(BaseModel):
    """Partial update (PATCH). Omitted fields are left unchanged."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    name: str | None = Field(None, min_length=1, max_length=255)
    calories: float | None = Field(None, ge=0)
    protein: float | None = Field(None, ge=0)
    carbs: float | None = Field(None, ge=0)
    fat: float | None = Field(None, ge=0)
    serving_size: float | None = Field(None, gt=0, alias="servingSize")
    serving_unit: str | None = Field(None, min_length=1, max_length=32, alias="servingUnit")

    @field_validator("name")
    @classmethod
    def name_stripped(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            raise ValueError("name must not be empty")
        return s

    @field_validator("serving_unit")
    @classmethod
    def unit_stripped(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            raise ValueError("servingUnit must not be empty")
        return s
