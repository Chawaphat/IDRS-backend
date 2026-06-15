from __future__ import annotations

import uuid
from datetime import datetime, timezone

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


def get_residual_ridge_assessment_by_chart_id(
    session: Session, chart_id: uuid.UUID
) -> ResidualRidgeAssessment | None:
    """Return the chart's assessment, or None if it doesn't exist yet.

    A missing record is a normal state for a fresh chart, so callers (GET endpoint)
    can treat None as "empty" instead of an error.
    """
    statement = select(ResidualRidgeAssessment).where(ResidualRidgeAssessment.chart_id == chart_id)
    return session.exec(statement).first()


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
    updates = payload.model_dump(exclude_unset=True)

    if item is None:
        item = ResidualRidgeAssessment.model_validate({**updates, "chart_id": chart_id})
    else:
        for key, value in updates.items():
            setattr(item, key, value)
        item.updated_at = datetime.now(timezone.utc)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_residual_ridge_assessment(session: Session, chart_id: uuid.UUID) -> None:
    item = get_residual_ridge_assessment_by_chart_id(session, chart_id)
    if item is not None:
        session.delete(item)
        session.commit()
