from __future__ import annotations

import uuid

from sqlmodel import Session, select

from app.models.occlusal_analysis import OcclusalAnalysis
from app.models.occlusal_contact import OcclusalContact,  OcclusalContactBulkCreate



def get_or_create_occlusal_analysis(session: Session, chart_id: uuid.UUID) -> OcclusalAnalysis:
    statement = select(OcclusalAnalysis).where(OcclusalAnalysis.chart_id == chart_id)
    occlusal = session.exec(statement).first()
    if not occlusal:
        occlusal = OcclusalAnalysis(chart_id=chart_id)
        session.add(occlusal)
        session.commit()
        session.refresh(occlusal)
    return occlusal

def create_and_replace_occlusal_contacts(
    session: Session,
    chart_id: uuid.UUID,
    payload: OcclusalContactBulkCreate,
) -> list[OcclusalContact]:
    occlusal = get_or_create_occlusal_analysis(session, chart_id)
    
    # ลบของเก่าทั้งหมดของ occlusal นี้
    old_contacts = session.exec(
        select(OcclusalContact).where(OcclusalContact.occlusal_id == occlusal.occlusal_id)
    ).all()
    for contact in old_contacts:
        session.delete(contact)
    
    # insert ใหม่ทั้งหมด
    items = [
        OcclusalContact(occlusal_id=occlusal.occlusal_id, **contact.model_dump())
        for contact in payload.contacts
    ]
    session.add_all(items)
    session.commit()
    return items 

def delete_occlusal_contact(session: Session, contact_id: uuid.UUID) -> None:
    
    item = session.get(OcclusalContact, contact_id)
    session.delete(item)
    session.commit()
