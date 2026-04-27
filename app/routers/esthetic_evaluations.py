from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.models.esthetic_evaluation import (
    EstheticEvaluation,
    EstheticEvaluationCreate,
    EstheticEvaluationUpdate,
)
from app.services.esthetic_evaluation import (
    create_esthetic_evaluation,
    delete_esthetic_evaluation,
    get_all_esthetic_evaluations,
    get_esthetic_evaluation_by_chart_id,
    get_esthetic_evaluation_by_id,
    update_esthetic_evaluation,
)

router = APIRouter()
admin_router = APIRouter()


@router.post("", response_model=EstheticEvaluation, status_code=status.HTTP_201_CREATED)
def create_esthetic_evaluation_endpoint(
    chart_id: uuid.UUID,
    payload: EstheticEvaluationCreate,
    session: Session = Depends(get_session),
) -> EstheticEvaluation:
    return create_esthetic_evaluation(session, chart_id, payload)


@router.get("", response_model=EstheticEvaluation, status_code=status.HTTP_200_OK)
def get_esthetic_evaluation_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> EstheticEvaluation:
    return get_esthetic_evaluation_by_chart_id(session, chart_id)


@router.put("", response_model=dict[str, Any], status_code=status.HTTP_200_OK)
def update_esthetic_evaluation_endpoint(
    chart_id: uuid.UUID,
    payload: EstheticEvaluationUpdate,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    item = update_esthetic_evaluation(session, chart_id, payload)

    return {
        "esthetic_id": item.esthetic_id,
        "chart_id": item.chart_id,
        **updates,
    }


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_esthetic_evaluation_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    delete_esthetic_evaluation(session, chart_id)


@admin_router.get("", response_model=list[EstheticEvaluation])
def get_all_esthetic_evaluations_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[EstheticEvaluation]:
    return get_all_esthetic_evaluations(session, skip=skip, limit=limit)


@admin_router.get("/{esthetic_id}", response_model=EstheticEvaluation)
def get_esthetic_evaluation_by_id_endpoint(
    esthetic_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> EstheticEvaluation:
    item = get_esthetic_evaluation_by_id(session, esthetic_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Esthetic evaluation not found")
    return item
