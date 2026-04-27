from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.esthetic_evaluation import (
    EstheticEvaluation,
    EstheticEvaluationCreate,
    EstheticEvaluationUpdate,
)


def create_esthetic_evaluation(
    session: Session,
    chart_id: uuid.UUID,
    payload: EstheticEvaluationCreate,
) -> EstheticEvaluation:
    item = EstheticEvaluation.model_validate({**payload.model_dump(), "chart_id": chart_id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_esthetic_evaluation_by_id(session: Session, esthetic_id: uuid.UUID) -> EstheticEvaluation | None:
    return session.get(EstheticEvaluation, esthetic_id)


def get_esthetic_evaluation_by_chart_id(session: Session, chart_id: uuid.UUID) -> EstheticEvaluation:
    statement = select(EstheticEvaluation).where(EstheticEvaluation.chart_id == chart_id)
    item = session.exec(statement).first()
    if not item:
        raise HTTPException(status_code=404, detail="Esthetic evaluation not found")
    return item


def get_all_esthetic_evaluations(
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[EstheticEvaluation]:
    statement = select(EstheticEvaluation).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_esthetic_evaluation(
    session: Session,
    chart_id: uuid.UUID,
    payload: EstheticEvaluationUpdate,
) -> EstheticEvaluation:
    item = get_esthetic_evaluation_by_chart_id(session, chart_id)
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updates.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_esthetic_evaluation(session: Session, chart_id: uuid.UUID) -> None:
    item = get_esthetic_evaluation_by_chart_id(session, chart_id)
    session.delete(item)
    session.commit()
