from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.models.dental_chart import DentalChart
from app.services.patient import (
    create_patient,
    delete_patient,
    get_all_patients,
    get_patient_by_id,
    get_patient_dental_charts,
    update_patient,
)
from app.models.patient import Patient, PatientCreate, PatientUpdate

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("", response_model=Patient, status_code=status.HTTP_201_CREATED)
def create_patient_endpoint(
    # Client จะส่งข้อมูลคนไข้มาในรูปแบบ JSON ซึ่งจะถูกแปลงเป็น instance ของ PatientCreate โดย FastAPI อัตโนมัติผ่านการใช้ Pydantic model ที่เราได้กำหนดไว้ใน PatientCreate
    payload: PatientCreate,
    session: Session = Depends(get_session),
) -> Patient:
    return create_patient(session, payload)
# -> Patient คือ - บอกว่า function นี้จะ return object ที่เป็น instance ของ Patient model ซึ่งช่วยให้ FastAPI สามารถสร้าง schema สำหรับ response ได้อัตโนมัติ และยังช่วยในการตรวจสอบ type ของข้อมูลที่ return ว่าตรงกับที่กำหนดไว้หรือไม่

@router.get("", response_model=list[Patient])
def get_patients_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[Patient]:
    return get_all_patients(session, skip=skip, limit=limit)


@router.get("/{patient_id}", response_model=Patient)
def get_patient_by_id_endpoint(
    patient_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> Patient:
    patient = get_patient_by_id(session, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.get("/{patient_id}/dental-charts", response_model=list[DentalChart])
def get_patient_dental_charts_endpoint(
    patient_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> list[DentalChart]:
    charts = get_patient_dental_charts(session, patient_id)
    if not charts:
        raise HTTPException(status_code=404, detail="Dental chart not found")
    return charts

@router.put("/{patient_id}", response_model=Patient)
def update_patient_endpoint(
    patient_id: uuid.UUID,
    payload: PatientUpdate,
    session: Session = Depends(get_session),
) -> Patient:
    patient = get_patient_by_id(session, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return update_patient(session, patient, payload)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_endpoint(
    patient_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    patient = get_patient_by_id(session, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    delete_patient(session, patient)
