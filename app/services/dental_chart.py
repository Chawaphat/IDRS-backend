from __future__ import annotations

import uuid
from typing import Any

from sqlmodel import Session, select

from app.models.dental_chart import DentalChart, DentalChartCreate, DentalChartUpdate
from app.models.dental_status import DentalStatus
from app.models.occlusal_analysis import OcclusalAnalysis
from app.models.occlusal_contact import OcclusalContact
from app.models.tooth import Tooth
from app.models.tooth_surface import ToothSurface


def create_dental_chart(session: Session, payload: DentalChartCreate) -> DentalChart:
    chart = DentalChart.model_validate(payload)
    session.add(chart)
    session.commit()
    session.refresh(chart)
    return chart

def get_dental_chart_by_id(session: Session, chart_id: uuid.UUID) -> DentalChart | None:
    return session.get(DentalChart, chart_id)

def get_all_dental_charts(session: Session, skip: int = 0, limit: int = 100) -> list[DentalChart]:
    statement = select(DentalChart).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def update_dental_chart(session: Session, chart: DentalChart, payload: DentalChartUpdate) -> DentalChart:
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(chart, key, value)
    session.add(chart)
    session.commit()
    session.refresh(chart)
    return chart

def delete_dental_chart(session: Session, chart: DentalChart) -> None:
    session.delete(chart)
    session.commit()


