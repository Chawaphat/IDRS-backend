from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.dental_status import (
    create_or_replace_dental_status,
    delete_dental_status,
    get_dental_status_by_chart_id,
)
from app.schemas.dental_status import DentalStatusBulkCreate, DentalStatusResponse

router = APIRouter()


@router.put("", response_model=DentalStatusResponse, status_code=status.HTTP_200_OK)
def create_dental_status_endpoint(
    payload: DentalStatusBulkCreate,
    chart_id: uuid.UUID,    
    session: Session = Depends(get_session),
) -> DentalStatusResponse:
    return create_or_replace_dental_status(session,chart_id,payload)

@router.get("", response_model=DentalStatusResponse, status_code=status.HTTP_200_OK)
def get_dental_status_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> DentalStatusResponse | None:
    return get_dental_status_by_chart_id(session, chart_id)

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_dental_status_endpoint(
    status_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    return delete_dental_status(session, status_id)
    
    