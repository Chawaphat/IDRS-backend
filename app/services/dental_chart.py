from __future__ import annotations

from fastapi import HTTPException
import uuid
from sqlmodel import Session, select

from app.models.dental_chart import DentalChart, DentalChartCreate, DentalChartUpdate

def create_dental_chart(session: Session, payload: DentalChartCreate) -> DentalChart:
    chart = DentalChart.model_validate(payload)
    session.add(chart)
    session.commit()
    session.refresh(chart)
    return chart

def get_dental_chart_by_id(session: Session, chart_id: uuid.UUID) -> DentalChart | None:
    chart = session.get(DentalChart, chart_id)
    if not chart:
        raise HTTPException(status_code=404, detail="Dental chart not found")
    return chart

def get_all_dental_charts(session: Session, skip: int = 0, limit: int = 100) -> list[DentalChart]:
    statement = select(DentalChart).offset(skip).limit(limit)
    if not session.exec(statement).first():
        raise HTTPException(status_code=404, detail="No dental charts found")
    return list(session.exec(statement).all())

def update_dental_chart(session: Session, chart_id: uuid.UUID, payload: DentalChartUpdate) -> DentalChart:
    chart = get_dental_chart_by_id(session, chart_id)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(chart, key, value)
    session.add(chart)
    session.commit()
    session.refresh(chart)
    return chart

def delete_dental_chart(session: Session, chart_id: uuid.UUID) -> None:
    chart = get_dental_chart_by_id(session, chart_id)
    session.delete(chart)
    session.commit()


