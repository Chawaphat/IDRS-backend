from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlmodel import Session, select ,or_

from app.models.dental_chart import DentalChart
from app.models.patient import Patient, PatientCreate, PatientUpdate, PatientWithClinicalSummary



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

from app.models.medical_histories import MedicalHistory

def get_all_patients(session: Session, skip: int = 0, limit: int = 100) -> list[PatientWithClinicalSummary]:
    statement = select(Patient).offset(skip).limit(limit)
    patients = session.exec(statement).all()
    
    results = []
    for p in patients:
        chart_stmt = select(DentalChart).where(DentalChart.patient_id == p.patient_id).order_by(DentalChart.record_date.desc())
        latest_chart = session.exec(chart_stmt).first()
        
        last_visit = latest_chart.record_date if latest_chart else None
        chief_complaint = None
        
        if latest_chart:
            mh_stmt = select(MedicalHistory).where(MedicalHistory.chart_id == latest_chart.chart_id)
            mh = session.exec(mh_stmt).first()
            if mh:
                chief_complaint = mh.chief_complaint
                
        results.append(PatientWithClinicalSummary(
            **p.model_dump(),
            last_visit=last_visit,
            chief_complaint=chief_complaint,
            status="Active"
        ))
    return results


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

def search_patients(
    session: Session,
    query: str,
    skip: int = 0,
    limit: int = 100,
) -> list[PatientWithClinicalSummary]:
    search_term = f"%{query}%"
    statement = (
        select(Patient)
        .where(
            or_(
                Patient.name.ilike(search_term),
                Patient.hn_number.ilike(search_term),
            )
        )
        .offset(skip)
        .limit(limit)
    )
    patients = session.exec(statement).all()
    
    results = []
    for p in patients:
        chart_stmt = select(DentalChart).where(DentalChart.patient_id == p.patient_id).order_by(DentalChart.record_date.desc())
        latest_chart = session.exec(chart_stmt).first()
        
        last_visit = latest_chart.record_date if latest_chart else None
        chief_complaint = None
        
        if latest_chart:
            mh_stmt = select(MedicalHistory).where(MedicalHistory.chart_id == latest_chart.chart_id)
            mh = session.exec(mh_stmt).first()
            if mh:
                chief_complaint = mh.chief_complaint
                
        results.append(PatientWithClinicalSummary(
            **p.model_dump(),
            last_visit=last_visit,
            chief_complaint=chief_complaint,
            status="Active"
        ))
    return results