from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.medical_histories import MedicalHistory, MedicalHistoryCreate, MedicalHistoryUpdate

def create_medical_history(session: Session, chart_id: uuid.UUID, payload: MedicalHistoryCreate) -> MedicalHistory:
    item = MedicalHistory.model_validate({**payload.model_dump(), "chart_id": chart_id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

def get_medical_history_by_id(session: Session, history_id: uuid.UUID) -> MedicalHistory | None:
    return session.get(MedicalHistory, history_id)

def get_medical_history_by_chart_id(session: Session, chart_id: uuid.UUID) -> MedicalHistory:
    statement = select(MedicalHistory).where(MedicalHistory.chart_id == chart_id)
    item = session.exec(statement).first()
    if not item:
        raise HTTPException(status_code=404, detail="Medical history not found")
    return item

def get_all_medical_histories(session: Session, skip: int = 0, limit: int = 100) -> list[MedicalHistory]:
    statement = select(MedicalHistory).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def update_medical_history(
    session: Session,
    chart_id: uuid.UUID,
    payload: MedicalHistoryUpdate,
) -> MedicalHistory:
    item = get_medical_history_by_chart_id(session, chart_id)
    
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updates.items():
        setattr(item, key, value)
    
    session.add(item)
    session.commit()
    session.refresh(item)
    
    return item

def delete_medical_history(session: Session, chart_id: uuid.UUID) -> None:
    item = get_medical_history_by_chart_id(session, chart_id)
    session.delete(item)
    session.commit()