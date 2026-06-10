from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.authen import get_current_profile
from app.models.profile import Profile
from app.models.dental_chart import DentalChart
from app.services.patient import (
    create_patient,
    delete_patient,
    get_all_patients,
    get_patient_by_id,
    get_patient_dental_charts,
    update_patient,
    search_patients,
)
from app.models.patient import Patient, PatientCreate, PatientUpdate, PatientWithClinicalSummary

router = APIRouter()

@router.post("", response_model=Patient, status_code=status.HTTP_201_CREATED)
def create_patient_endpoint(
    payload: PatientCreate,
    session: Session = Depends(get_session),
    current_user: Profile = Depends(get_current_profile),
) -> Patient:
    return create_patient(session, payload, current_user.id)

@router.get("", response_model=list[PatientWithClinicalSummary])
def get_patients_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
    current_user: Profile = Depends(get_current_profile),
) -> list[PatientWithClinicalSummary]:
    return get_all_patients(session, current_user.id, skip=skip, limit=limit)

@router.get("/search", response_model=list[PatientWithClinicalSummary])
def search_patients_endpoint(
    query: str = Query(..., min_length=1, description="Search by name or HN number"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
    current_user: Profile = Depends(get_current_profile),
):
    return search_patients(session, query=query, dentist_id=current_user.id, skip=skip, limit=limit)

@router.get("/{patient_id}", response_model=Patient)
def get_patient_by_id_endpoint(
    patient_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: Profile = Depends(get_current_profile),
) -> Patient:
    return get_patient_by_id(session, patient_id, current_user.id)

@router.get("/{patient_id}/dental-charts", response_model=list[DentalChart])
def get_patient_dental_charts_endpoint(
    patient_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> list[DentalChart]:
    return get_patient_dental_charts(session, patient_id)

@router.put("/{patient_id}", response_model=Patient)
def update_patient_endpoint(
    patient_id: uuid.UUID,
    payload: PatientUpdate,
    session: Session = Depends(get_session),
    current_user: Profile = Depends(get_current_profile),
) -> Patient:
    return update_patient(session, patient_id, payload, current_user.id)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_endpoint(
    patient_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: Profile = Depends(get_current_profile),
) -> None:
    delete_patient(session, patient_id, current_user.id)
