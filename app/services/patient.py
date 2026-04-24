from __future__ import annotations

import uuid

from sqlmodel import Session, select

from app.models.patient import Patient, PatientCreate, PatientUpdate



def create_patient(session: Session, payload: PatientCreate) -> Patient:
    patient = Patient.model_validate(payload)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


def get_patient_by_id(session: Session, patient_id: uuid.UUID) -> Patient | None:
    return session.get(Patient, patient_id)


def get_all_patients(session: Session, skip: int = 0, limit: int = 100) -> list[Patient]:
    statement = select(Patient).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_patient(session: Session, patient: Patient, payload: PatientUpdate) -> Patient:
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(patient, key, value)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


def delete_patient(session: Session, patient: Patient) -> None:
    session.delete(patient)
    session.commit()
