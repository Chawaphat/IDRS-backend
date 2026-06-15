from __future__ import annotations

import uuid

from sqlmodel import Session, select

from app.models.extraoral_exam import ExtraoralExam, ExtraoralExamCreate, ExtraoralExamUpdate


def create_extraoral_exam(session: Session, chart_id: uuid.UUID, payload: ExtraoralExamCreate) -> ExtraoralExam:
    item = ExtraoralExam.model_validate({**payload.model_dump(), "chart_id": chart_id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_extraoral_exam_by_id(session: Session, exam_id: uuid.UUID) -> ExtraoralExam | None:
    return session.get(ExtraoralExam, exam_id)


def get_extraoral_exam_by_chart_id(session: Session, chart_id: uuid.UUID) -> ExtraoralExam | None:
    """Return the chart's extraoral exam, or None if it doesn't exist yet.

    A missing record is normal for a fresh chart, so the GET endpoint can return
    None (empty) instead of a 404 that the UI would surface as an error.
    """
    statement = select(ExtraoralExam).where(ExtraoralExam.chart_id == chart_id)
    return session.exec(statement).first()


def get_all_extraoral_exams(session: Session, skip: int = 0, limit: int = 100) -> list[ExtraoralExam]:
    statement = select(ExtraoralExam).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_extraoral_exam(
    session: Session,
    chart_id: uuid.UUID,
    payload: ExtraoralExamUpdate,
) -> ExtraoralExam:
    """Upsert the chart's extraoral exam: update if it exists, otherwise create it.

    Uses exclude_unset (NOT exclude_none) so an explicit null clears a field instead
    of leaving the previously saved value in place.
    """
    item = session.exec(
        select(ExtraoralExam).where(ExtraoralExam.chart_id == chart_id)
    ).first()
    updates = payload.model_dump(exclude_unset=True)

    if item is None:
        item = ExtraoralExam.model_validate({**updates, "chart_id": chart_id})
    else:
        for key, value in updates.items():
            setattr(item, key, value)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_extraoral_exam(session: Session, chart_id: uuid.UUID) -> None:
    item = get_extraoral_exam_by_chart_id(session, chart_id)
    if item is not None:
        session.delete(item)
        session.commit()
