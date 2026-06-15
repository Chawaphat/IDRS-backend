from __future__ import annotations

import uuid

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


def get_vdo_evaluation_by_chart_id(session: Session, chart_id: uuid.UUID) -> VdoEvaluation | None:
    """Return the chart's VDO evaluation, or None if it doesn't exist yet.

    A missing record is normal for a fresh chart, so the GET endpoint can return
    None (empty) instead of a 404 that the UI would surface as an error.
    """
    statement = select(VdoEvaluation).where(VdoEvaluation.chart_id == chart_id)
    return session.exec(statement).first()


def get_all_vdo_evaluations(session: Session, skip: int = 0, limit: int = 100) -> list[VdoEvaluation]:
    statement = select(VdoEvaluation).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_vdo_evaluation(
    session: Session,
    chart_id: uuid.UUID,
    payload: VdoEvaluationUpdate,
) -> VdoEvaluation:
    """Upsert the chart's VDO evaluation: update if it exists, otherwise create it.

    Uses exclude_unset (NOT exclude_none) so an explicit null clears a field instead
    of leaving the previously saved value in place.
    """
    item = session.exec(
        select(VdoEvaluation).where(VdoEvaluation.chart_id == chart_id)
    ).first()
    updates = payload.model_dump(exclude_unset=True)

    if item is None:
        item = VdoEvaluation.model_validate({**updates, "chart_id": chart_id})
    else:
        for key, value in updates.items():
            setattr(item, key, value)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_vdo_evaluation(session: Session, chart_id: uuid.UUID) -> None:
    item = get_vdo_evaluation_by_chart_id(session, chart_id)
    if item is not None:
        session.delete(item)
        session.commit()
