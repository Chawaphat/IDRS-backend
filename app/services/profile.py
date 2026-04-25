from __future__ import annotations

import uuid

from sqlmodel import Session, select

from app.models.dental_chart import DentalChart
from app.models.profile import Profile, ProfileCreate, ProfileUpdate

def create_profile(session: Session, payload: ProfileCreate) -> Profile:
    profile = Profile.model_validate(payload)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def get_profile_by_id(session: Session, profile_id: uuid.UUID) -> Profile | None:
    return session.get(Profile, profile_id)


def get_all_profiles(session: Session, skip: int = 0, limit: int = 100) -> list[Profile]:
    statement = select(Profile).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def get_profile_dental_charts(session: Session, dentist_id: uuid.UUID) -> list[DentalChart]:
    statement = select(DentalChart).where(DentalChart.dentist_id == dentist_id)
    return list(session.exec(statement).all())

def update_profile(session: Session, profile: Profile, payload: ProfileUpdate) -> Profile:
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(profile, key, value)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def delete_profile(session: Session, profile: Profile) -> None:
    session.delete(profile)
    session.commit()
