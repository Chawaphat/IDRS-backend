from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.residual_ridge_assessment import (
    ResidualRidgeAssessment,
    ResidualRidgeAssessmentCreate,
    ResidualRidgeAssessmentUpdate,
)


def create_residual_ridge_assessment(
    session: Session,
    chart_id: uuid.UUID,
    payload: ResidualRidgeAssessmentCreate,
) -> ResidualRidgeAssessment:
    item = ResidualRidgeAssessment.model_validate({**payload.model_dump(), "chart_id": chart_id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_residual_ridge_assessment_by_id(session: Session, assessment_id: uuid.UUID) -> ResidualRidgeAssessment | None:
    return session.get(ResidualRidgeAssessment, assessment_id)


def get_residual_ridge_assessment_by_chart_id(session: Session, chart_id: uuid.UUID) -> ResidualRidgeAssessment:
    statement = select(ResidualRidgeAssessment).where(ResidualRidgeAssessment.chart_id == chart_id)
    item = session.exec(statement).first()
    if not item:
        raise HTTPException(status_code=404, detail="Residual ridge assessment not found")
    return item


def get_all_residual_ridge_assessments(
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[ResidualRidgeAssessment]:
    statement = select(ResidualRidgeAssessment).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_residual_ridge_assessment(
    session: Session,
    chart_id: uuid.UUID,
    payload: ResidualRidgeAssessmentUpdate,
) -> ResidualRidgeAssessment:
    statement = select(ResidualRidgeAssessment).where(ResidualRidgeAssessment.chart_id == chart_id)
    item = session.exec(statement).first()
    if not item:
        item = ResidualRidgeAssessment.model_validate(
            {**payload.model_dump(exclude_unset=True, exclude_none=True), "chart_id": chart_id}
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updates.items():
        setattr(item, key, value)
    item.updated_at = datetime.utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_residual_ridge_assessment(session: Session, chart_id: uuid.UUID) -> None:
    item = get_residual_ridge_assessment_by_chart_id(session, chart_id)
    session.delete(item)
    session.commit()
