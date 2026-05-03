from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import WeightEntry
from app.deps import CurrentUser, DbSession, verify_app_bearer
from app.schemas.weight_entry import WeightEntryCreate, WeightEntryRead, WeightEntryUpdate

router = APIRouter(
    prefix="/me/weight-entries",
    tags=["weight-entries"],
    dependencies=[Depends(verify_app_bearer)],
)

_PATCH_TO_ORM: dict[str, str] = {
    "logged_date": "logged_date",
    "weight_kg": "weight_kg",
}


def _to_read(m: WeightEntry) -> WeightEntryRead:
    return WeightEntryRead(
        id=m.id,
        logged_date=m.logged_date,
        weight_kg=float(m.weight_kg),
    )


def _get_owned(db: Session, user_id: str, entry_id: str) -> WeightEntry | None:
    row = db.get(WeightEntry, entry_id)
    if row is None or row.user_id != user_id:
        return None
    return row


@router.get("", response_model=list[WeightEntryRead])
def list_weight_entries(
    user: CurrentUser,
    db: DbSession,
    logged_date: date | None = Query(
        default=None,
        alias="date",
        description="If set, return only the entry for this calendar day (YYYY-MM-DD).",
    ),
    date_from: date | None = Query(
        default=None,
        alias="from",
        description="Inclusive start date. Ignored if `date` is set.",
    ),
    date_to: date | None = Query(
        default=None,
        alias="to",
        description="Inclusive end date. Ignored if `date` is set.",
    ),
) -> list[WeightEntryRead]:
    q = select(WeightEntry).where(WeightEntry.user_id == user.id)
    if logged_date is not None:
        q = q.where(WeightEntry.logged_date == logged_date)
    else:
        if date_from is not None:
            q = q.where(WeightEntry.logged_date >= date_from)
        if date_to is not None:
            q = q.where(WeightEntry.logged_date <= date_to)
    q = q.order_by(WeightEntry.logged_date.desc())
    rows = db.scalars(q).all()
    return [_to_read(m) for m in rows]


@router.post("", response_model=WeightEntryRead)
def create_or_replace_weight_entry(user: CurrentUser, db: DbSession, body: WeightEntryCreate) -> WeightEntryRead:
    """Insert a row or update ``weight_kg`` if this user already has a row for ``date``."""
    existing = db.scalar(
        select(WeightEntry).where(
            WeightEntry.user_id == user.id,
            WeightEntry.logged_date == body.logged_date,
        )
    )
    if existing is not None:
        existing.weight_kg = body.weight_kg
        db.add(existing)
        db.flush()
        return _to_read(existing)
    eid = str(uuid.uuid4())
    row = WeightEntry(
        id=eid,
        user_id=user.id,
        logged_date=body.logged_date,
        weight_kg=body.weight_kg,
    )
    db.add(row)
    try:
        db.flush()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not save weight entry (duplicate day). Try again or PATCH the existing id.",
        ) from err
    return _to_read(row)


@router.get("/{entry_id}", response_model=WeightEntryRead)
def get_weight_entry(user: CurrentUser, db: DbSession, entry_id: str) -> WeightEntryRead:
    row = _get_owned(db, user.id, entry_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weight entry not found")
    return _to_read(row)


@router.patch("/{entry_id}", response_model=WeightEntryRead)
def patch_weight_entry(
    user: CurrentUser, db: DbSession, entry_id: str, body: WeightEntryUpdate
) -> WeightEntryRead:
    row = _get_owned(db, user.id, entry_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weight entry not found")
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
            status_code=status.HTTP_409_CONFLICT,
            detail="Another entry already exists for that date.",
        ) from err
    return _to_read(row)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weight_entry(user: CurrentUser, db: DbSession, entry_id: str) -> None:
    row = _get_owned(db, user.id, entry_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weight entry not found")
    db.delete(row)
    db.flush()
