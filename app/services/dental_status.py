from __future__ import annotations

from typing import Any
import uuid

from sqlmodel import Session, select

from app.models.dental_status import DentalStatus
from app.models.tooth import Tooth
from app.models.tooth_surface import ToothSurface

from app.schemas.dental_status import DentalStatusBulkCreate , DentalStatusResponse , ToothResponse , ToothSurfaceResponse


def create_or_replace_dental_status(
    session: Session,
    chart_id: uuid.UUID,
    payload: DentalStatusBulkCreate,
) -> DentalStatusResponse:
    statement = select(DentalStatus).where(DentalStatus.chart_id == chart_id)
    status = session.exec(statement).first()

    if not status:
        status = DentalStatus(chart_id=chart_id)
        session.add(status)
        session.commit()
        session.refresh(status)

    old_teeth = session.exec(
        select(Tooth).where(Tooth.status_id == status.status_id)
    ).all()

    for t in old_teeth:
        session.delete(t)

    session.flush()

    for tooth_data in payload.teeth:
        tooth = Tooth(
            status_id=status.status_id,
            tooth_number=tooth_data.tooth_number,
            tooth_status=tooth_data.tooth_status, 
            tooth_detail=tooth_data.tooth_detail,  
            crown=tooth_data.crown,
            root_status=tooth_data.root_status,
        )
        session.add(tooth)
        session.flush()  

        for s in tooth_data.surfaces:
            surface = ToothSurface(
                tooth_id=tooth.tooth_id,
                surface=s.surface,
                condition=s.condition,
            )
            session.add(surface)

    session.commit()
    return status


def get_dental_status_by_chart_id(
    session: Session, chart_id: uuid.UUID
) -> DentalStatusResponse | None:

    status_stmt = (
        select(DentalStatus)
        .where(DentalStatus.chart_id == chart_id)
        .order_by(DentalStatus.created_at.desc())
    )
    status_record = session.exec(status_stmt).first()

    if status_record is None:
        return None

    teeth_stmt = select(Tooth).where(Tooth.status_id == status_record.status_id)
    teeth = list(session.exec(teeth_stmt).all())

    if not teeth:
        return DentalStatusResponse(
            status_id=status_record.status_id,
            chart_id=status_record.chart_id,
            created_at=status_record.created_at,
            teeth=[],
        )

    tooth_ids = [t.tooth_id for t in teeth]

    surfaces_stmt = select(ToothSurface).where(
        ToothSurface.tooth_id.in_(tooth_ids)
    )
    all_surfaces = list(session.exec(surfaces_stmt).all())

    
    surface_map: dict[uuid.UUID, list[ToothSurface]] = {}
    for s in all_surfaces:
        surface_map.setdefault(s.tooth_id, []).append(s)

   
    result_teeth: list[ToothResponse] = []

    for tooth in teeth:
        surfaces = surface_map.get(tooth.tooth_id, [])

        result_teeth.append(
            ToothResponse(
                tooth_id=tooth.tooth_id,
                tooth_number=tooth.tooth_number,
                tooth_status=tooth.tooth_status,
                tooth_detail=tooth.tooth_detail,
                crown=tooth.crown,
                root_status=tooth.root_status,
                surfaces=[
                    ToothSurfaceResponse(
                        surface_id=s.surface_id,
                        surface=s.surface,
                        condition=s.condition,
                    )
                    for s in surfaces
                ],
            )
        )

    return DentalStatusResponse(
        status_id=status_record.status_id,
        chart_id=status_record.chart_id,
        created_at=status_record.created_at,
        teeth=result_teeth,
    )
    


def delete_dental_status(session: Session, status_id: uuid.UUID) -> None:
    statement = select(DentalStatus).where(DentalStatus.status_id == status_id)
    status = session.exec(statement).first()
    if status:
        session.delete(status)
        session.commit()