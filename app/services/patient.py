from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.dental_chart import DentalChart
from app.models.patient import Patient, PatientCreate, PatientUpdate



def create_patient(session: Session, payload: PatientCreate) -> Patient:
    patient = Patient.model_validate(payload)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


def get_patient_by_id(session: Session, patient_id: uuid.UUID) -> Patient:
    patient = session.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

def get_patient_dental_charts(session: Session, patient_id: uuid.UUID) -> list[DentalChart]:
    statement = select(DentalChart).where(DentalChart.patient_id == patient_id)
    if not session.exec(statement).first():
        raise HTTPException(status_code=404, detail="Dental charts not found for this patient")
    return list(session.exec(statement).all())

def get_all_patients(session: Session, skip: int = 0, limit: int = 100) -> list[Patient]:
    statement = select(Patient).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_patient(session: Session, patient_id: uuid.UUID, payload: PatientUpdate) -> Patient:
    patient = get_patient_by_id(session, patient_id)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(patient, key, value)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


def delete_patient(session: Session, patient_id: uuid.UUID) -> None:
    patient = get_patient_by_id(session, patient_id)
    session.delete(patient)
    session.commit()
