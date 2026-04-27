from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter , Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.medical_histories import (
    create_medical_history,
    delete_medical_history,
    get_all_medical_histories,
    get_medical_history_by_chart_id,
    get_medical_history_by_id,
    update_medical_history,
)
from app.models.medical_histories import MedicalHistory, MedicalHistoryCreate, MedicalHistoryUpdate

router = APIRouter()
admin_router = APIRouter()

# Endpoints for medical histories linked to a dental chart
@router.post("", response_model=MedicalHistory, status_code=status.HTTP_201_CREATED)
def create_medical_history_endpoint(
    chart_id: uuid.UUID,
    payload: MedicalHistoryCreate,
    session: Session = Depends(get_session),
) -> MedicalHistory:
    return create_medical_history(session, chart_id, payload)

@router.get("", response_model=MedicalHistory, status_code=status.HTTP_200_OK)
def get_medical_histories_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> MedicalHistory:
    return get_medical_history_by_chart_id(session, chart_id)

@router.put("", response_model=dict[str, Any], status_code=status.HTTP_200_OK)
def update_medical_history_endpoint(
    chart_id: uuid.UUID,
    payload: MedicalHistoryUpdate,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    item = update_medical_history(session, chart_id, payload)

    return {
        "history_id": item.history_id,
        "chart_id": item.chart_id,
         **updates
    }

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_medical_history_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    delete_medical_history(session, chart_id)
    
# Admin endpoints for medical histories 
@admin_router.get("", response_model=list[MedicalHistory])
def get_all_medical_histories_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[MedicalHistory]:
    return get_all_medical_histories(session, skip=skip, limit=limit)

@admin_router.get("/{history_id}", response_model=MedicalHistory)
def get_medical_history_by_id_endpoint(
    history_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> MedicalHistory:
    item = get_medical_history_by_id(session, history_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Medical history not found")
    return item 