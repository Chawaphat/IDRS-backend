from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.models.residual_ridge_assessment import (
    ResidualRidgeAssessment,
    ResidualRidgeAssessmentCreate,
    ResidualRidgeAssessmentUpdate,
)
from app.services.residual_ridge_assessment import (
    create_residual_ridge_assessment,
    delete_residual_ridge_assessment,
    get_all_residual_ridge_assessments,
    get_residual_ridge_assessment_by_chart_id,
    get_residual_ridge_assessment_by_id,
    update_residual_ridge_assessment,
)

router = APIRouter()
admin_router = APIRouter()


@router.post("", response_model=ResidualRidgeAssessment, status_code=status.HTTP_201_CREATED)
def create_residual_ridge_assessment_endpoint(
    chart_id: uuid.UUID,
    payload: ResidualRidgeAssessmentCreate,
    session: Session = Depends(get_session),
) -> ResidualRidgeAssessment:
    return create_residual_ridge_assessment(session, chart_id, payload)


@router.get("", response_model=ResidualRidgeAssessment | None, status_code=status.HTTP_200_OK)
def get_residual_ridge_assessment_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ResidualRidgeAssessment | None:
    return get_residual_ridge_assessment_by_chart_id(session, chart_id)


@router.put("", response_model=ResidualRidgeAssessment, status_code=status.HTTP_200_OK)
def update_residual_ridge_assessment_endpoint(
    chart_id: uuid.UUID,
    payload: ResidualRidgeAssessmentUpdate,
    session: Session = Depends(get_session),
) -> ResidualRidgeAssessment:
    return update_residual_ridge_assessment(session, chart_id, payload)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_residual_ridge_assessment_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    delete_residual_ridge_assessment(session, chart_id)


@admin_router.get("", response_model=list[ResidualRidgeAssessment])
def get_all_residual_ridge_assessments_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[ResidualRidgeAssessment]:
    return get_all_residual_ridge_assessments(session, skip=skip, limit=limit)


@admin_router.get("/{assessment_id}", response_model=ResidualRidgeAssessment)
def get_residual_ridge_assessment_by_id_endpoint(
    assessment_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ResidualRidgeAssessment:
    item = get_residual_ridge_assessment_by_id(session, assessment_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Residual ridge assessment not found")
    return item