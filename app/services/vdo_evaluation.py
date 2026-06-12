from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.vdo_evaluation import VdoEvaluation, VdoEvaluationCreate, VdoEvaluationUpdate


def create_vdo_evaluation(session: Session, chart_id: uuid.UUID, payload: VdoEvaluationCreate) -> VdoEvaluation:
    item = VdoEvaluation.model_validate({**payload.model_dump(), "chart_id": chart_id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_vdo_evaluation_by_id(session: Session, vdo_id: uuid.UUID) -> VdoEvaluation | None:
    return session.get(VdoEvaluation, vdo_id)


def get_vdo_evaluation_by_chart_id(session: Session, chart_id: uuid.UUID) -> VdoEvaluation:
    statement = select(VdoEvaluation).where(VdoEvaluation.chart_id == chart_id)
    item = session.exec(statement).first()
    if not item:
        raise HTTPException(status_code=404, detail="VDO evaluation not found")
    return item


def get_all_vdo_evaluations(session: Session, skip: int = 0, limit: int = 100) -> list[VdoEvaluation]:
    statement = select(VdoEvaluation).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_vdo_evaluation(
    session: Session,
    chart_id: uuid.UUID,
    payload: VdoEvaluationUpdate,
) -> VdoEvaluation:
    statement = select(VdoEvaluation).where(VdoEvaluation.chart_id == chart_id)
    item = session.exec(statement).first()
    if not item:
        item = VdoEvaluation.model_validate(
            {**payload.model_dump(exclude_unset=True, exclude_none=True), "chart_id": chart_id}
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updates.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_vdo_evaluation(session: Session, chart_id: uuid.UUID) -> None:
    item = get_vdo_evaluation_by_chart_id(session, chart_id)
    session.delete(item)
    session.commit()
