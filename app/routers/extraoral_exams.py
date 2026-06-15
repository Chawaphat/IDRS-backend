from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.extraoral_exam import (
    create_extraoral_exam,
    delete_extraoral_exam,
    get_all_extraoral_exams,
    get_extraoral_exam_by_id,
    get_extraoral_exam_by_chart_id,
    update_extraoral_exam,
)
from app.models.extraoral_exam import ExtraoralExam, ExtraoralExamCreate, ExtraoralExamUpdate

router = APIRouter()
admin_router = APIRouter()

# Endpoints for extraoral exams linked to a dental chart
@router.post("", response_model=ExtraoralExam, status_code=status.HTTP_201_CREATED)
def create_extraoral_exam_endpoint(
    chart_id: uuid.UUID,
    payload: ExtraoralExamCreate,
    session: Session = Depends(get_session),
) -> ExtraoralExam:
    return create_extraoral_exam(session,chart_id, payload)


@router.get("", response_model=ExtraoralExam | None, status_code=status.HTTP_200_OK)
def get_extraoral_exams_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ExtraoralExam | None:
    return get_extraoral_exam_by_chart_id(session, chart_id)

@router.put("", response_model=ExtraoralExam, status_code=status.HTTP_200_OK)
def update_extraoral_exam_endpoint(
    chart_id: uuid.UUID,
    payload: ExtraoralExamUpdate,
    session: Session = Depends(get_session),
) -> ExtraoralExam:
    return update_extraoral_exam(session, chart_id, payload)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_extraoral_exam_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    delete_extraoral_exam(session, chart_id)

# Admin endpoints for extraoral exams
@admin_router.get("", response_model=list[ExtraoralExam])
def get_all_extraoral_exams_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[ExtraoralExam]:
    return get_all_extraoral_exams(session, skip=skip, limit=limit)

@admin_router.get("/{exam_id}", response_model=ExtraoralExam)
def get_extraoral_exam_by_id_endpoint(
    exam_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ExtraoralExam:
    item = get_extraoral_exam_by_id(session,exam_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Extraoral exam not found")
    return item