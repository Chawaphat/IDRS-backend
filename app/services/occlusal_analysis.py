from __future__ import annotations

from typing import Any
import uuid

from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.occlusal_analysis import (
    OcclusalAnalysis,
    OcclusalAnalysisCreate,
)
from app.models.occlusal_contact import OcclusalContact
from app.models.enums import ContactType

def upsert_occlusal_analysis(session: Session, chart_id: uuid.UUID, payload: OcclusalAnalysisCreate) -> OcclusalAnalysis:
    statement = select(OcclusalAnalysis).where(OcclusalAnalysis.chart_id == chart_id)
    occlusal = session.exec(statement).first()
    
    if occlusal:
        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(occlusal, key, value)
    else:
        occlusal = OcclusalAnalysis(chart_id=chart_id, **payload.model_dump())
    
    session.add(occlusal)
    session.commit()
    session.refresh(occlusal)
    return occlusal
        
def get_occlusal_analysis_by_id(session: Session, occlusal_id: uuid.UUID) -> OcclusalAnalysis | None:
    return session.get(OcclusalAnalysis, occlusal_id)

def get_occlusal_analysis_by_chart_id(session: Session, chart_id: uuid.UUID) -> OcclusalAnalysis:
    statement = select(OcclusalAnalysis).where(OcclusalAnalysis.chart_id == chart_id)
    item = session.exec(statement).first()
    if not item:
        raise HTTPException(status_code=404, detail="Occlusal analysis not found")
    return item

def get_all_occlusal_analyses(
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[OcclusalAnalysis]:
    statement = select(OcclusalAnalysis).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def delete_occlusal_analysis(session: Session, chart_id: uuid.UUID) -> None:
    item = get_occlusal_analysis_by_chart_id(session, chart_id)
    session.delete(item)
    session.commit()


def get_occlusal_analysis_record(session: Session, chart_id: uuid.UUID) -> dict[str, Any] | None:
    occlusal = get_occlusal_analysis_by_chart_id(session, chart_id)  # ← ใช้ function เดิมที่มี 404 อยู่แล้ว ไม่ต้อง query ซ้ำ

    contacts = list(session.exec(
        select(OcclusalContact).where(OcclusalContact.occlusal_id == occlusal.occlusal_id)
    ).all())

    grouped: dict[str, list] = {ct.value: [] for ct in ContactType}
    for contact in contacts:
        grouped[contact.contact_type.value].append({
            "contact_id": contact.contact_id,
            "upper_tooth": contact.upper_tooth,
            "lower_tooth": contact.lower_tooth,
        })
        
    return {
        "occlusal_id": occlusal.occlusal_id,
        "chart_id": occlusal.chart_id,
        "right_molar": occlusal.right_molar,
        "left_molar": occlusal.left_molar,
        "overlap_horizontal": occlusal.overlap_horizontal,
        "overlap_vertical": occlusal.overlap_vertical,
        "anterior_slide": occlusal.anterior_slide,
        "lateral_slide": occlusal.lateral_slide,
        "contacts": grouped
    }
