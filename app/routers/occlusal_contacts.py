from __future__ import annotations

from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.occlusal_contact import (
    create_occlusal_contact,
    delete_occlusal_contact,
    get_all_occlusal_contacts,
    get_occlusal_contact_by_id,
    update_occlusal_contact,
    
)
from app.models.occlusal_contact import OcclusalContact, OcclusalContactCreate, OcclusalContactUpdate

router = APIRouter(prefix="/occlusal-contacts/{chart_id}", tags=["occlusal-contacts"])


@router.post("", response_model=OcclusalContact, status_code=status.HTTP_201_CREATED)
def create_occlusal_contact_endpoint(
    chart_id: uuid.UUID,
    payload: OcclusalContactCreate,
    session: Session = Depends(get_session),
) -> OcclusalContact:
    return create_occlusal_contact(session, chart_id, payload)


@router.get("", response_model=list[OcclusalContact])
def get_occlusal_contacts_endpoint(
    chart_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[OcclusalContact]:
    return get_all_occlusal_contacts(session, skip=skip, limit=limit)


@router.get("/{contact_id}", response_model=OcclusalContact)
def get_occlusal_contact_by_id_endpoint(
    contact_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> OcclusalContact:
    item = get_occlusal_contact_by_id(session, contact_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Occlusal contact not found")
    return item


@router.put("/{contact_id}", response_model=OcclusalContact)
def update_occlusal_contact_endpoint(
    contact_id: uuid.UUID,
    payload: OcclusalContactUpdate,
    session: Session = Depends(get_session),
) -> OcclusalContact:
    item = get_occlusal_contact_by_id(session, contact_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Occlusal contact not found")
    return update_occlusal_contact(session, item, payload)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_occlusal_contact_endpoint(
    contact_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    item = get_occlusal_contact_by_id(session, contact_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Occlusal contact not found")
    delete_occlusal_contact(session, item)


