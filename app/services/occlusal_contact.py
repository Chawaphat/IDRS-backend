from __future__ import annotations

import uuid

from sqlmodel import Session, select

from app.models.occlusal_analysis import OcclusalAnalysis
from app.models.occlusal_contact import OcclusalContact, OcclusalContactCreate, OcclusalContactUpdate


def create_occlusal_contact(session: Session, chart_id: uuid.UUID, payload: OcclusalContactCreate) -> OcclusalContact:
    
    statement = select(OcclusalAnalysis).where(OcclusalAnalysis.chart_id == chart_id)
    occlusal = session.exec(statement).first()
        
    if not occlusal:
        occlusal = OcclusalAnalysis(chart_id=chart_id)
        session.add(occlusal)
        session.commit()
        session.refresh(occlusal)

    item = OcclusalContact.model_validate({**payload.model_dump(), "occlusal_id": occlusal.occlusal_id})    
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_occlusal_contact_by_id(session: Session, contact_id: uuid.UUID) -> OcclusalContact | None:
    return session.get(OcclusalContact, contact_id)


def get_all_occlusal_contacts(
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[OcclusalContact]:
    statement = select(OcclusalContact).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_occlusal_contact(
    session: Session,
    item: OcclusalContact,
    payload: OcclusalContactUpdate,
) -> OcclusalContact:
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_occlusal_contact(session: Session, item: OcclusalContact) -> None:
    session.delete(item)
    session.commit()
