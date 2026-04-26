from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.dental_chart import (
    create_dental_chart,
    delete_dental_chart,
    get_all_dental_charts,
    get_dental_chart_by_id,
    update_dental_chart,
)
from app.models.dental_chart import DentalChart, DentalChartCreate, DentalChartUpdate

router = APIRouter()


@router.post("", response_model=DentalChart, status_code=status.HTTP_201_CREATED)
def create_dental_chart_endpoint(
    payload: DentalChartCreate,
    session: Session = Depends(get_session),
) -> DentalChart:
    return create_dental_chart(session, payload)


@router.get("", response_model=list[DentalChart])
def get_dental_charts_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[DentalChart]:
    return get_all_dental_charts(session, skip=skip, limit=limit)


@router.get("/{chart_id}", response_model=DentalChart)
def get_dental_chart_by_id_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> DentalChart:
    return get_dental_chart_by_id(session, chart_id)

@router.put("/{chart_id}", response_model=DentalChart)
def update_dental_chart_endpoint(
    chart_id: uuid.UUID,
    payload: DentalChartUpdate,
    session: Session = Depends(get_session),
) -> DentalChart:
    return update_dental_chart(session, chart_id, payload)


@router.delete("/{chart_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dental_chart_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    delete_dental_chart(session, chart_id)


