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


def get_esthetic_evaluation_by_chart_id(session: Session, chart_id: uuid.UUID) -> EstheticEvaluation | None:
    statement = select(EstheticEvaluation).where(EstheticEvaluation.chart_id == chart_id)
    return session.exec(statement).first()


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
    statement = select(EstheticEvaluation).where(EstheticEvaluation.chart_id == chart_id)
    item = session.exec(statement).first()

    if not item:
        # Create a new item if it doesn't exist
        create_payload = EstheticEvaluationCreate(**payload.model_dump(exclude_unset=True, exclude_none=True))
        item = EstheticEvaluation.model_validate({**create_payload.model_dump(), "chart_id": chart_id})
        session.add(item)
    else:
        # Update existing item
        updates = payload.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in updates.items():
            setattr(item, key, value)
        session.add(item)
        
    session.commit()
    session.refresh(item)
    return item


def delete_esthetic_evaluation(session: Session, chart_id: uuid.UUID) -> None:
    item = get_esthetic_evaluation_by_chart_id(session, chart_id)
    if item:
        session.delete(item)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="Esthetic evaluation not found")
