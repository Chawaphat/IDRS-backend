from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.dental_chart import DentalChart
from app.models.occlusal_analysis import OcclusalAnalysis
from app.models.occlusal_contact import OcclusalContact, OcclusalContactBulkCreate
from app.services.occlusal_analysis import get_occlusal_analysis_by_chart_id



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
    if session.get(DentalChart, chart_id) is None:
        raise HTTPException(status_code=404, detail="Chart not found")
    occlusal = get_or_create_occlusal_analysis(session, chart_id)

    existing = list(session.exec(
        select(OcclusalContact).where(OcclusalContact.occlusal_id == occlusal.occlusal_id)
    ).all())
    for contact in existing:
        session.delete(contact)

    # insert ใหม่ทั้งหมด
    items = [
        OcclusalContact(occlusal_id=occlusal.occlusal_id, **contact.model_dump())
        for contact in payload.contacts
    ]
    session.add_all(items)
    session.commit()
    return items 


def get_occlusal_contacts_by_chart_id(
    session: Session,
    chart_id: uuid.UUID,
) -> list[OcclusalContact]:
    try:
        occlusal = get_occlusal_analysis_by_chart_id(session, chart_id)
    except HTTPException as exc:
        if exc.status_code == 404:
            return []
        raise

    return list(session.exec(
        select(OcclusalContact).where(OcclusalContact.occlusal_id == occlusal.occlusal_id)
    ).all())

def delete_occlusal_contact(session: Session, contact_id: uuid.UUID) -> None:
    item = session.get(OcclusalContact, contact_id)
    session.delete(item)
    session.commit()
