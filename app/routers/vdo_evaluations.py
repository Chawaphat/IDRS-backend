from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.models.vdo_evaluation import VdoEvaluation, VdoEvaluationCreate, VdoEvaluationUpdate
from app.services.vdo_evaluation import (
    create_vdo_evaluation,
    delete_vdo_evaluation,
    get_all_vdo_evaluations,
    get_vdo_evaluation_by_chart_id,
    get_vdo_evaluation_by_id,
    update_vdo_evaluation,
)

router = APIRouter()
admin_router = APIRouter()


@router.post("", response_model=VdoEvaluation, status_code=status.HTTP_201_CREATED)
def create_vdo_evaluation_endpoint(
    chart_id: uuid.UUID,
    payload: VdoEvaluationCreate,
    session: Session = Depends(get_session),
) -> VdoEvaluation:
    return create_vdo_evaluation(session, chart_id, payload)


@router.get("", response_model=VdoEvaluation, status_code=status.HTTP_200_OK)
def get_vdo_evaluation_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> VdoEvaluation:
    return get_vdo_evaluation_by_chart_id(session, chart_id)


@router.put("", response_model=dict[str, Any], status_code=status.HTTP_200_OK)
def update_vdo_evaluation_endpoint(
    chart_id: uuid.UUID,
    payload: VdoEvaluationUpdate,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    item = update_vdo_evaluation(session, chart_id, payload)

    return {
        "vdo_id": item.vdo_id,
        "chart_id": item.chart_id,
        **updates,
    }


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_vdo_evaluation_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    delete_vdo_evaluation(session, chart_id)


@admin_router.get("", response_model=list[VdoEvaluation])
def get_all_vdo_evaluations_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[VdoEvaluation]:
    return get_all_vdo_evaluations(session, skip=skip, limit=limit)


@admin_router.get("/{vdo_id}", response_model=VdoEvaluation)
def get_vdo_evaluation_by_id_endpoint(
    vdo_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> VdoEvaluation:
    item = get_vdo_evaluation_by_id(session, vdo_id)
    if item is None:
        raise HTTPException(status_code=404, detail="VDO evaluation not found")
    return item
