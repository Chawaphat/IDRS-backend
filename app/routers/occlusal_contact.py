from __future__ import annotations

from typing import Any
import uuid

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.occlusal_contact import (
    
    delete_occlusal_contact,
    create_and_replace_occlusal_contacts
)
from app.models.occlusal_contact import OcclusalContact, OcclusalContactBulkCreate

router = APIRouter()

@router.put("", response_model=list[OcclusalContact], status_code=status.HTTP_200_OK)
def replace_occlusal_contacts_endpoint(
    chart_id: uuid.UUID,
    payload: OcclusalContactBulkCreate,
    session: Session = Depends(get_session),
) -> list[OcclusalContact]:
    return create_and_replace_occlusal_contacts(session, chart_id, payload)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_occlusal_contact_endpoint(
    contact_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    delete_occlusal_contact(session, contact_id)

