from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.medical_histories import MedicalHistory, MedicalHistoryCreate, MedicalHistoryUpdate

from app.models.dental_chart import DentalChart
from app.models.patient import Patient

def create_medical_history(session: Session, chart_id: uuid.UUID, payload: MedicalHistoryCreate) -> MedicalHistory:
    chart = session.get(DentalChart, chart_id)
    if chart is None:
        raise HTTPException(status_code=404, detail="Chart not found")
    item = MedicalHistory.model_validate({**payload.model_dump(), "chart_id": chart_id})
    session.add(item)

    # Sync allergy to patient
    if chart:
        patient = session.get(Patient, chart.patient_id)
        if patient:
            if item.allergy_status == "yes" and item.allergy_detail:
                patient.allergy = item.allergy_detail
            elif item.allergy_status in ["no", "dont_know"]:
                patient.allergy = None
            session.add(patient)

    session.commit()
    session.refresh(item)
    return item

def get_medical_history_by_id(session: Session, history_id: uuid.UUID) -> MedicalHistory | None:
    return session.get(MedicalHistory, history_id)

def get_medical_history_by_chart_id(session: Session, chart_id: uuid.UUID) -> MedicalHistory:
    statement = select(MedicalHistory).where(MedicalHistory.chart_id == chart_id)
    item = session.exec(statement).first()
    if item is None:
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
    # Upsert with exclude_unset (NOT exclude_none) so an explicit null clears a field.
    item = session.exec(
        select(MedicalHistory).where(MedicalHistory.chart_id == chart_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Medical history not found")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(item, key, value)
    session.add(item)

    # Sync allergy to patient
    chart = session.get(DentalChart, chart_id)
    if chart:
        patient = session.get(Patient, chart.patient_id)
        if patient:
            if item.allergy_status == "yes" and item.allergy_detail:
                patient.allergy = item.allergy_detail
            elif item.allergy_status in ["no", "dont_know"]:
                patient.allergy = None
            session.add(patient)

    session.commit()
    session.refresh(item)
    return item

def delete_medical_history(session: Session, chart_id: uuid.UUID) -> None:
    item = get_medical_history_by_chart_id(session, chart_id)
    if item is not None:
        session.delete(item)
        session.commit()