from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, or_

from app.models.dental_chart import DentalChart
from app.models.patient import Patient, PatientCreate, PatientUpdate, PatientWithClinicalSummary


def _activity_sort_key(item: PatientWithClinicalSummary) -> datetime:
    """Sort key for the patient directory: most recent activity first.

    Uses the patient's last visit if they have a chart, otherwise when they were
    registered (created_at) — so both active patients and brand-new registrations
    surface at the top. tzinfo is stripped so naive (utcnow default) and tz-aware
    (read back from Postgres) timestamps stay comparable in one list.
    """
    when = item.last_visit or item.created_at
    if when.tzinfo is not None:
        when = when.replace(tzinfo=None)
    return when



def create_patient(session: Session, payload: PatientCreate, dentist_id: uuid.UUID) -> Patient:
    patient = Patient.model_validate(payload)
    patient.dentist_id = dentist_id
    session.add(patient)
    try:
        session.commit()
    except IntegrityError:
        # Duplicate hn_number violates the unique constraint — return a
        # client-friendly error (SRS-72) instead of a raw 500.
        session.rollback()
        raise HTTPException(status_code=409, detail="Hospital Number already exists")
    session.refresh(patient)
    return patient


def get_patient_by_id(session: Session, patient_id: uuid.UUID, dentist_id: uuid.UUID) -> Patient:
    patient = session.get(Patient, patient_id)
    if patient is None or patient.dentist_id != dentist_id:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

def get_patient_dental_charts(session: Session, patient_id: uuid.UUID) -> list[DentalChart]:
    statement = select(DentalChart).where(DentalChart.patient_id == patient_id)
    charts = list(session.exec(statement).all())
    if not charts:
        raise HTTPException(status_code=404, detail="Dental charts not found for this patient")
    return charts

from app.models.medical_histories import MedicalHistory

def _with_clinical_summaries(
    session: Session,
    patients: list[Patient],
) -> list[PatientWithClinicalSummary]:
    if not patients:
        return []

    patient_ids = [patient.patient_id for patient in patients]
    charts = list(session.exec(
        select(DentalChart)
        .where(DentalChart.patient_id.in_(patient_ids))
        .order_by(DentalChart.record_date.desc())
    ).all())

    latest_charts: dict[uuid.UUID, DentalChart] = {}
    for chart in charts:
        latest_charts.setdefault(chart.patient_id, chart)

    chart_ids = [chart.chart_id for chart in latest_charts.values()]
    histories_by_chart_id: dict[uuid.UUID, MedicalHistory] = {}
    if chart_ids:
        histories_by_chart_id = {
            history.chart_id: history
            for history in session.exec(
                select(MedicalHistory).where(MedicalHistory.chart_id.in_(chart_ids))
            ).all()
        }

    results = []
    for patient in patients:
        latest_chart = latest_charts.get(patient.patient_id)
        history = (
            histories_by_chart_id.get(latest_chart.chart_id)
            if latest_chart else None
        )
        patient_data = patient.model_dump()

        if history:
            if history.allergy_status == "yes" and history.allergy_detail:
                patient_data["allergy"] = history.allergy_detail
            elif history.allergy_status in ["no", "dont_know"]:
                patient_data["allergy"] = None

        results.append(PatientWithClinicalSummary(
            **patient_data,
            last_visit=latest_chart.record_date if latest_chart else None,
            chief_complaint=history.chief_complaint if history else None,
            status="Active",
        ))

    results.sort(key=_activity_sort_key, reverse=True)
    return results


def get_all_patients(session: Session, dentist_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[PatientWithClinicalSummary]:
    statement = select(Patient).where(Patient.dentist_id == dentist_id).offset(skip).limit(limit)
    patients = list(session.exec(statement).all())
    return _with_clinical_summaries(session, patients)


def update_patient(session: Session, patient_id: uuid.UUID, payload: PatientUpdate, dentist_id: uuid.UUID) -> Patient:
    patient = get_patient_by_id(session, patient_id, dentist_id)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(patient, key, value)
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


def delete_patient(session: Session, patient_id: uuid.UUID, dentist_id: uuid.UUID) -> None:
    patient = get_patient_by_id(session, patient_id, dentist_id)
    session.delete(patient)
    session.commit()

def search_patients(
    session: Session,
    query: str,
    dentist_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[PatientWithClinicalSummary]:
    search_term = f"%{query}%"
    statement = (
        select(Patient)
        .where(Patient.dentist_id == dentist_id)
        .where(
            or_(
                Patient.name.ilike(search_term),
                Patient.hn_number.ilike(search_term),
            )
        )
        .offset(skip)
        .limit(limit)
    )
    patients = list(session.exec(statement).all())
    return _with_clinical_summaries(session, patients)