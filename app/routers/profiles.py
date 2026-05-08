from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from app.core.security import get_current_profile ,require_admin , require_profile_owner

from app.core.database import get_session
from app.models.dental_chart import DentalChart
from app.services.profile import (
    create_profile,
    delete_profile,
    get_all_profiles,
    get_profile_by_id,
    get_profile_dental_charts,
    update_profile,
)
from app.models.profile import Profile, ProfileCreate, ProfileUpdate

router = APIRouter()


@router.post("", response_model=Profile, status_code=status.HTTP_201_CREATED)
def create_profile_endpoint(
    payload: ProfileCreate,
    session: Session = Depends(get_session),
    current_user: Profile = Depends(require_admin)
) -> Profile:
    return create_profile(session, payload)


@router.get("", response_model=list[Profile])
def get_profiles_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
    current_user: Profile = Depends(require_admin),
) -> list[Profile]:
    
    return get_all_profiles(
        session,
        skip=skip,
        limit=limit
    )


@router.get("/me")
def get_me(
    current_user: Profile = Depends(get_current_profile)
):
    return current_user

@router.get("/{profile_id}", response_model=Profile)
def get_profile_by_id_endpoint(
    profile_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: Profile = Depends(require_profile_owner),
) -> Profile:
    return get_profile_by_id(session, profile_id)

@router.get("/{profile_id}/dental-charts", response_model=list[DentalChart])
def get_profile_dental_charts_endpoint(
    profile_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: Profile = Depends(require_profile_owner),
) -> list[DentalChart]:    
    return get_profile_dental_charts(session, profile_id)

@router.put("/{profile_id}", response_model=Profile)
def update_profile_endpoint(
    profile_id: uuid.UUID,
    payload: ProfileUpdate,
    session: Session = Depends(get_session),
    current_user: Profile = Depends(require_profile_owner),
) -> Profile:
    return update_profile(session, profile_id, payload)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile_endpoint(
    profile_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: Profile = Depends(require_admin),
) -> None:
    delete_profile(session, profile_id)
