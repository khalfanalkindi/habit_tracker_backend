from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import FoodLogEntry, FoodOption
from app.deps import CurrentUser, DbSession, verify_app_bearer
from app.schemas.food_log_entry import FoodLogEntryCreate, FoodLogEntryRead, FoodLogEntryUpdate

router = APIRouter(
    prefix="/me/food-log-entries",
    tags=["food-log-entries"],
    dependencies=[Depends(verify_app_bearer)],
)

_PATCH_TO_ORM: dict[str, str] = {
    "log_date": "log_date",
    "food_option_id": "food_option_id",
    "meal_type": "meal_type",
    "quantity": "quantity",
}


def _to_read(m: FoodLogEntry) -> FoodLogEntryRead:
    return FoodLogEntryRead(
        id=m.id,
        log_date=m.log_date,
        food_option_id=m.food_option_id,
        meal_type=m.meal_type,
        quantity=float(m.quantity),
    )


def _get_owned(db: Session, user_id: str, entry_id: str) -> FoodLogEntry | None:
    row = db.get(FoodLogEntry, entry_id)
    if row is None or row.user_id != user_id:
        return None
    return row


def _ensure_food_option_owned(db: Session, user_id: str, food_option_id: str) -> None:
    fo = db.get(FoodOption, food_option_id)
    if fo is None or fo.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="foodOptionId must reference an existing food option that belongs to you",
        )


@router.get("", response_model=list[FoodLogEntryRead])
def list_food_log_entries(
    user: CurrentUser,
    db: DbSession,
    date: date | None = Query(
        default=None,
        description="If set, return only entries for this calendar day (YYYY-MM-DD).",
    ),
    date_from: date | None = Query(
        default=None,
        alias="from",
        description="Inclusive start date (YYYY-MM-DD). Ignored if `date` is set.",
    ),
    date_to: date | None = Query(
        default=None,
        alias="to",
        description="Inclusive end date (YYYY-MM-DD). Ignored if `date` is set.",
    ),
) -> list[FoodLogEntryRead]:
    q = select(FoodLogEntry).where(FoodLogEntry.user_id == user.id)
    if date is not None:
        q = q.where(FoodLogEntry.log_date == date)
    else:
        if date_from is not None:
            q = q.where(FoodLogEntry.log_date >= date_from)
        if date_to is not None:
            q = q.where(FoodLogEntry.log_date <= date_to)
    q = q.order_by(FoodLogEntry.log_date.desc(), FoodLogEntry.created_at.desc())
    rows = db.scalars(q).all()
    return [_to_read(m) for m in rows]


@router.post("", response_model=FoodLogEntryRead, status_code=status.HTTP_201_CREATED)
def create_food_log_entry(user: CurrentUser, db: DbSession, body: FoodLogEntryCreate) -> FoodLogEntryRead:
    _ensure_food_option_owned(db, user.id, body.food_option_id)
    eid = str(uuid.uuid4())
    row = FoodLogEntry(
        id=eid,
        user_id=user.id,
        food_option_id=body.food_option_id,
        log_date=body.log_date,
        meal_type=body.meal_type,
        quantity=body.quantity,
    )
    db.add(row)
    try:
        db.flush()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create food log entry (check foodOptionId).",
        ) from err
    return _to_read(row)


@router.get("/{entry_id}", response_model=FoodLogEntryRead)
def get_food_log_entry(user: CurrentUser, db: DbSession, entry_id: str) -> FoodLogEntryRead:
    row = _get_owned(db, user.id, entry_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food log entry not found")
    return _to_read(row)


@router.patch("/{entry_id}", response_model=FoodLogEntryRead)
def patch_food_log_entry(
    user: CurrentUser, db: DbSession, entry_id: str, body: FoodLogEntryUpdate
) -> FoodLogEntryRead:
    row = _get_owned(db, user.id, entry_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food log entry not found")
    if "food_option_id" in body.model_fields_set and body.food_option_id is not None:
        _ensure_food_option_owned(db, user.id, body.food_option_id)
    for fname in body.model_fields_set:
        orm_attr = _PATCH_TO_ORM.get(fname)
        if orm_attr is None:
            continue
        val = getattr(body, fname)
        if val is None:
            continue
        setattr(row, orm_attr, val)
    try:
        db.flush()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update food log entry (check foodOptionId).",
        ) from err
    return _to_read(row)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_log_entry(user: CurrentUser, db: DbSession, entry_id: str) -> None:
    row = _get_owned(db, user.id, entry_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food log entry not found")
    db.delete(row)
    db.flush()
