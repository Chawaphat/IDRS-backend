from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.authen import get_current_profile, verify_token
from app.core.database import get_session
from app.models.profile import Profile, ProfileCreate, ProfileUpdate
from app.services.profile import create_profile, delete_profile, update_profile

router = APIRouter()


@router.get("/me", response_model=Profile)
def get_me(
    current_user: Profile = Depends(get_current_profile),
) -> Profile:
    """Return the currently authenticated user's profile."""
    return current_user


@router.post(
    "/register-profile",
    response_model=Profile,
    status_code=status.HTTP_201_CREATED,
)
def register_profile(
    payload: ProfileCreate,
    session: Session = Depends(get_session),
    token_payload: dict = Depends(verify_token),
) -> Profile:
    """
    Create a profile for the authenticated user on first login / after Supabase signup.
    Safe to call multiple times — returns existing profile if one already exists.
    """
    user_id = uuid.UUID(token_payload["sub"])

    # Upsert: return existing profile if already created
    existing = session.get(Profile, user_id)
    if existing:
        return existing

    return create_profile(session, payload, user_id)


@router.put("/me", response_model=Profile)
def update_me(
    payload: ProfileUpdate,
    session: Session = Depends(get_session),
    current_user: Profile = Depends(get_current_profile),
) -> Profile:
    """Update the authenticated user's own profile."""
    return update_profile(session, current_user.id, payload)


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(
    session: Session = Depends(get_session),
    current_user: Profile = Depends(get_current_profile),
) -> None:
    """Delete the authenticated user's own account/profile."""
    delete_profile(session, current_user.id)
