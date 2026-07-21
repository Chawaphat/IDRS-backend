from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.dental_chart import DentalChart
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
    if session.get(DentalChart, chart_id) is None:
        raise HTTPException(status_code=404, detail="Chart not found")
    item = ResidualRidgeAssessment.model_validate({**payload.model_dump(), "chart_id": chart_id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_residual_ridge_assessment_by_id(session: Session, assessment_id: uuid.UUID) -> ResidualRidgeAssessment | None:
    return session.get(ResidualRidgeAssessment, assessment_id)


def get_residual_ridge_assessment_by_chart_id(
    session: Session, chart_id: uuid.UUID
) -> ResidualRidgeAssessment:
    statement = select(ResidualRidgeAssessment).where(ResidualRidgeAssessment.chart_id == chart_id)
    item = session.exec(statement).first()
    if item is None:
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
    """Upsert the chart's assessment: update the existing row, or create it if missing.

    Uses exclude_unset (NOT exclude_none) so an explicit null clears a field — the
    client can erase a value it entered earlier instead of the old value sticking.
    """
    item = session.exec(
        select(ResidualRidgeAssessment).where(ResidualRidgeAssessment.chart_id == chart_id)
    ).first()
    if item is None:
        item = ResidualRidgeAssessment.model_validate({**payload.model_dump(), "chart_id": chart_id})
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(item, key, value)
    item.updated_at = datetime.now(timezone.utc)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_residual_ridge_assessment(session: Session, chart_id: uuid.UUID) -> None:
    item = get_residual_ridge_assessment_by_chart_id(session, chart_id)
    session.delete(item)
    session.commit()
