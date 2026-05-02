from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models import UserProfile
from app.deps import CurrentUser, DbSession, verify_api_key
from app.schemas.auth import UserPublic
from app.schemas.profile import ProfileRead, ProfileUpdate

router = APIRouter(prefix="/me", tags=["me"], dependencies=[Depends(verify_api_key)])


def _get_or_create_profile(db: Session, user_id: str) -> UserProfile:
    row = db.get(UserProfile, user_id)
    if row is None:
        row = UserProfile(user_id=user_id)
        db.add(row)
        db.flush()
    return row


def _profile_to_read(p: UserProfile) -> ProfileRead:
    return ProfileRead(
        heightM=float(p.height_m) if p.height_m is not None else None,
        weightKg=float(p.weight_kg) if p.weight_kg is not None else None,
        dailyCaloriesTarget=p.daily_calories_target,
        weightGoalKg=float(p.weight_goal_kg) if p.weight_goal_kg is not None else None,
        birthday=p.birthday,
        gender=p.gender,
    )


@router.get("", response_model=UserPublic)
def read_me(user: CurrentUser) -> UserPublic:
    return UserPublic(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        username=user.username,
    )


@router.get("/profile", response_model=ProfileRead)
def read_profile(user: CurrentUser, db: DbSession) -> ProfileRead:
    p = _get_or_create_profile(db, user.id)
    return _profile_to_read(p)


@router.put("/profile", response_model=ProfileRead)
def update_profile(user: CurrentUser, db: DbSession, body: ProfileUpdate) -> ProfileRead:
    p = _get_or_create_profile(db, user.id)
    data = body.model_dump(exclude_unset=True)
    for key in (
        "height_m",
        "weight_kg",
        "daily_calories_target",
        "weight_goal_kg",
        "birthday",
        "gender",
    ):
        if key in data:
            setattr(p, key, data[key])
    db.add(p)
    db.flush()
    return _profile_to_read(p)


@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(user: CurrentUser, db: DbSession) -> None:
    p = db.get(UserProfile, user.id)
    if p is not None:
        db.delete(p)
