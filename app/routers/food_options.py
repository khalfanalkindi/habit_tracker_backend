from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import FoodOption
from app.deps import CurrentUser, DbSession, verify_app_bearer
from app.schemas.food_option import FoodOptionCreate, FoodOptionRead, FoodOptionUpdate

router = APIRouter(
    prefix="/me/food-options",
    tags=["food-options"],
    dependencies=[Depends(verify_app_bearer)],
)

_PATCH_TO_ORM: dict[str, str] = {
    "name": "name",
    "calories": "calories_per_serving",
    "protein": "protein_g_per_serving",
    "carbs": "carbs_g_per_serving",
    "fat": "fat_g_per_serving",
    "serving_size": "serving_size",
    "serving_unit": "serving_unit",
}


def _to_read(m: FoodOption) -> FoodOptionRead:
    return FoodOptionRead(
        id=m.id,
        name=m.name,
        calories=float(m.calories_per_serving),
        protein=float(m.protein_g_per_serving),
        carbs=float(m.carbs_g_per_serving),
        fat=float(m.fat_g_per_serving),
        serving_size=float(m.serving_size),
        serving_unit=m.serving_unit,
    )


def _get_owned(db: Session, user_id: str, food_option_id: str) -> FoodOption | None:
    row = db.get(FoodOption, food_option_id)
    if row is None or row.user_id != user_id:
        return None
    return row


@router.get("", response_model=list[FoodOptionRead])
def list_food_options(user: CurrentUser, db: DbSession) -> list[FoodOptionRead]:
    rows = db.scalars(
        select(FoodOption)
        .where(FoodOption.user_id == user.id)
        .order_by(FoodOption.created_at.asc())
    ).all()
    return [_to_read(m) for m in rows]


@router.post("", response_model=FoodOptionRead, status_code=status.HTTP_201_CREATED)
def create_food_option(user: CurrentUser, db: DbSession, body: FoodOptionCreate) -> FoodOptionRead:
    fid = str(uuid.uuid4())
    row = FoodOption(
        id=fid,
        user_id=user.id,
        name=body.name,
        calories_per_serving=body.calories,
        protein_g_per_serving=body.protein,
        carbs_g_per_serving=body.carbs,
        fat_g_per_serving=body.fat,
        serving_size=body.serving_size,
        serving_unit=body.serving_unit,
    )
    db.add(row)
    db.flush()
    return _to_read(row)


@router.get("/{food_option_id}", response_model=FoodOptionRead)
def get_food_option(user: CurrentUser, db: DbSession, food_option_id: str) -> FoodOptionRead:
    row = _get_owned(db, user.id, food_option_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food option not found")
    return _to_read(row)


@router.patch("/{food_option_id}", response_model=FoodOptionRead)
def patch_food_option(
    user: CurrentUser, db: DbSession, food_option_id: str, body: FoodOptionUpdate
) -> FoodOptionRead:
    row = _get_owned(db, user.id, food_option_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food option not found")
    for fname in body.model_fields_set:
        orm_attr = _PATCH_TO_ORM.get(fname)
        if orm_attr is None:
            continue
        setattr(row, orm_attr, getattr(body, fname))
    db.add(row)
    db.flush()
    return _to_read(row)


@router.delete("/{food_option_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_option(user: CurrentUser, db: DbSession, food_option_id: str) -> None:
    row = _get_owned(db, user.id, food_option_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food option not found")
    try:
        db.delete(row)
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This food option is used by food log entries. Remove or change those logs first.",
        ) from None
