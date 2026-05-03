from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ExerciseEntry
from app.deps import CurrentUser, DbSession, verify_app_bearer
from app.schemas.exercise_entry import ExerciseEntryCreate, ExerciseEntryRead, ExerciseEntryUpdate

router = APIRouter(
    prefix="/me/exercise-entries",
    tags=["exercise-entries"],
    dependencies=[Depends(verify_app_bearer)],
)

_PATCH_TO_ORM: dict[str, str] = {
    "day_of_week": "day_of_week",
    "exercise_type": "exercise_type",
    "duration_minutes": "duration_minutes",
    "completed": "completed",
    "completed_on_date": "completed_on_date",
}


def _to_read(m: ExerciseEntry) -> ExerciseEntryRead:
    return ExerciseEntryRead(
        id=m.id,
        day_of_week=m.day_of_week,
        exercise_type=m.exercise_type,
        duration_minutes=m.duration_minutes,
        completed=bool(m.completed),
        completed_on_date=m.completed_on_date,
    )


def _get_owned(db: Session, user_id: str, entry_id: str) -> ExerciseEntry | None:
    row = db.get(ExerciseEntry, entry_id)
    if row is None or row.user_id != user_id:
        return None
    return row


@router.get("", response_model=list[ExerciseEntryRead])
def list_exercise_entries(
    user: CurrentUser,
    db: DbSession,
    day_of_week: int | None = Query(
        default=None,
        ge=0,
        le=6,
        alias="dayOfWeek",
        description="If set, return only entries for this weekday (0=Sunday … 6=Saturday).",
    ),
) -> list[ExerciseEntryRead]:
    q = select(ExerciseEntry).where(ExerciseEntry.user_id == user.id)
    if day_of_week is not None:
        q = q.where(ExerciseEntry.day_of_week == day_of_week)
    q = q.order_by(ExerciseEntry.day_of_week.asc(), ExerciseEntry.created_at.asc())
    rows = db.scalars(q).all()
    return [_to_read(m) for m in rows]


@router.post("", response_model=ExerciseEntryRead, status_code=status.HTTP_201_CREATED)
def create_exercise_entry(user: CurrentUser, db: DbSession, body: ExerciseEntryCreate) -> ExerciseEntryRead:
    eid = str(uuid.uuid4())
    row = ExerciseEntry(
        id=eid,
        user_id=user.id,
        day_of_week=body.day_of_week,
        exercise_type=body.exercise_type,
        duration_minutes=body.duration_minutes,
        completed=body.completed,
        completed_on_date=body.completed_on_date,
    )
    db.add(row)
    db.flush()
    return _to_read(row)


@router.get("/{entry_id}", response_model=ExerciseEntryRead)
def get_exercise_entry(user: CurrentUser, db: DbSession, entry_id: str) -> ExerciseEntryRead:
    row = _get_owned(db, user.id, entry_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise entry not found")
    return _to_read(row)


@router.patch("/{entry_id}", response_model=ExerciseEntryRead)
def patch_exercise_entry(
    user: CurrentUser, db: DbSession, entry_id: str, body: ExerciseEntryUpdate
) -> ExerciseEntryRead:
    row = _get_owned(db, user.id, entry_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise entry not found")
    for fname in body.model_fields_set:
        orm_attr = _PATCH_TO_ORM.get(fname)
        if orm_attr is None:
            continue
        val = getattr(body, fname)
        if val is None:
            if orm_attr in ("duration_minutes", "completed_on_date"):
                setattr(row, orm_attr, None)
            continue
        setattr(row, orm_attr, val)
    if "completed" in body.model_fields_set and body.completed is False:
        row.completed_on_date = None
    db.flush()
    return _to_read(row)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise_entry(user: CurrentUser, db: DbSession, entry_id: str) -> None:
    row = _get_owned(db, user.id, entry_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise entry not found")
    db.delete(row)
    db.flush()
