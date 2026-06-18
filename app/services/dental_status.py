# services/dental_status.py

import uuid
from fastapi import HTTPException
from sqlmodel import Session, select, delete
from app.models.dental_status import DentalStatus
from app.models.tooth_record import ToothRecord
from app.models.tooth_edentulous import ToothEdentulous
from app.models.tooth_caries import ToothCaries
from app.models.tooth_filling import ToothFilling
from app.models.tooth_periodontal import ToothPeriodontal
from app.models.tooth_vitality import ToothVitality
from app.models.tooth_restoration import ToothRestoration
from app.models.tooth_implant import ToothImplant
from app.schemas.dental_status import (
    DentalStatusBulkCreate, DentalStatusResponse,
    ToothResponse,
    EdentulousResponse, CariesResponse, FillingResponse,
    PeriodontalResponse, VitalityResponse, RestorationResponse,
    ImplantResponse,
)

TOOTH_CHILD_MODELS = (
    ToothEdentulous,
    ToothCaries,
    ToothFilling,
    ToothPeriodontal,
    ToothVitality,
    ToothRestoration,
    ToothImplant,
)


def _delete_teeth_for_status(session: Session, status_id: uuid.UUID) -> None:
    teeth = list(session.exec(
        select(ToothRecord).where(ToothRecord.status_id == status_id)
    ).all())

    if not teeth:
        return

    tooth_ids = [tooth.tooth_id for tooth in teeth]

    for model in TOOTH_CHILD_MODELS:
        session.exec(
            delete(model).where(model.tooth_id.in_(tooth_ids)).execution_options(synchronize_session=False)
        )

    session.exec(
        delete(ToothRecord).where(ToothRecord.tooth_id.in_(tooth_ids)).execution_options(synchronize_session=False)
    )


def _build_response(session: Session, status: DentalStatus) -> DentalStatusResponse:
    
    teeth = list(session.exec(
        select(ToothRecord).where(ToothRecord.status_id == status.status_id)
    ).all())

    if not teeth:
        return DentalStatusResponse(
            status_id=status.status_id,
            chart_id=status.chart_id,
            created_at=status.created_at,
            teeth=[],
        )

    tooth_ids = [t.tooth_id for t in teeth]

    
    edentulous_map: dict[uuid.UUID, ToothEdentulous] = {
        r.tooth_id: r for r in session.exec(
            select(ToothEdentulous).where(ToothEdentulous.tooth_id.in_(tooth_ids))
        ).all()
    }
    periodontal_map: dict[uuid.UUID, ToothPeriodontal] = {
        r.tooth_id: r for r in session.exec(
            select(ToothPeriodontal).where(ToothPeriodontal.tooth_id.in_(tooth_ids))
        ).all()
    }
    vitality_map: dict[uuid.UUID, ToothVitality] = {
        r.tooth_id: r for r in session.exec(
            select(ToothVitality).where(ToothVitality.tooth_id.in_(tooth_ids))
        ).all()
    }
    implant_map: dict[uuid.UUID, ToothImplant] = {
        r.tooth_id: r for r in session.exec(
            select(ToothImplant).where(ToothImplant.tooth_id.in_(tooth_ids))
        ).all()
    }

    restoration_map: dict[uuid.UUID, ToothRestoration] = {
        r.tooth_id: r for r in session.exec(
            select(ToothRestoration).where(ToothRestoration.tooth_id.in_(tooth_ids))
        ).all()
    }
    
    # 1-to-many → group by tooth_id
    caries_map: dict[uuid.UUID, list[ToothCaries]] = {}
    for r in session.exec(
        select(ToothCaries).where(ToothCaries.tooth_id.in_(tooth_ids))
    ).all():
        caries_map.setdefault(r.tooth_id, []).append(r)

    filling_map: dict[uuid.UUID, list[ToothFilling]] = {}
    for r in session.exec(
        select(ToothFilling).where(ToothFilling.tooth_id.in_(tooth_ids))
    ).all():
        filling_map.setdefault(r.tooth_id, []).append(r)


    # 3. Assemble response ต่อฟัน
    result_teeth: list[ToothResponse] = []

    for tooth in teeth:
        tid = tooth.tooth_id

        # 1-to-1
        e = edentulous_map.get(tid)
        pe = periodontal_map.get(tid)
        v = vitality_map.get(tid)
        im = implant_map.get(tid)
        r = restoration_map.get(tid)

        result_teeth.append(ToothResponse(
            tooth_id=tid,
            tooth_number=tooth.tooth_number,
            tooth_type=tooth.tooth_type,
            note=tooth.note,

            edentulous=EdentulousResponse(
                edentulous_id=e.edentulous_id,
                edentulous_type=e.edentulous_type,
                note=e.note,
            ) if e else None,

            periodontal=PeriodontalResponse(
                periodontal_id=pe.periodontal_id,
                mobility_grade=pe.mobility_grade,
                recession_mm=pe.recession_mm,
                note=pe.note,
            ) if pe else None,

            vitality=VitalityResponse(
                vitality_id=v.vitality_id,
                pulp_status=v.pulp_status,
                ept_result=v.ept_result,
                root_canal_treated=v.root_canal_treated,
                note=v.note,
            ) if v else None,

            implant=ImplantResponse(
                implant_id=im.implant_id,
                component_type=im.component_type,
                retention_type=im.retention_type,
                material=im.material,
                brand=im.brand,
                crown_brand=im.crown_brand,
                note=im.note,
            ) if im else None,
            
            restorations=(
                RestorationResponse(
                    restoration_id=r.restoration_id,
                    restoration_type=r.restoration_type,
                    material=r.material,
                    post_type=r.post_type,
                    note=r.note,
                )
            ) if r else None,
                

            # 1-to-many
            caries=[
                CariesResponse(
                    caries_id=c.caries_id,
                    surface=c.surface,
                    depth=c.depth,
                    note=c.note,
                )
                for c in caries_map.get(tid, [])
            ],

            fillings=[
                FillingResponse(
                    filling_id=f.filling_id,
                    surfaces=f.surfaces,  # JSONB list
                    material=f.material,
                    size_mm=f.size_mm,
                    note=f.note,
                )
                for f in filling_map.get(tid, [])
            ],
        ))

    return DentalStatusResponse(
        status_id=status.status_id,
        chart_id=status.chart_id,
        created_at=status.created_at,
        teeth=result_teeth,
    )



def create_or_replace_dental_status(
    session: Session,
    chart_id: uuid.UUID,
    payload: DentalStatusBulkCreate,
) -> DentalStatusResponse:

    
    status = session.exec(
        select(DentalStatus).where(DentalStatus.chart_id == chart_id)
    ).first()

    if not status:
        status = DentalStatus(chart_id=chart_id)
        session.add(status)
        session.flush()

    _delete_teeth_for_status(session, status.status_id)

    for td in payload.teeth:
        tooth = ToothRecord(
            status_id=status.status_id,
            tooth_number=td.tooth_number,
            tooth_type=td.tooth_type,
            note=td.note,
        )
        session.add(tooth)
        
        if td.edentulous:
            session.add(ToothEdentulous(tooth_id=tooth.tooth_id, **td.edentulous.model_dump()))
        if td.periodontal:
            session.add(ToothPeriodontal(tooth_id=tooth.tooth_id, **td.periodontal.model_dump()))
        if td.vitality:
            session.add(ToothVitality(tooth_id=tooth.tooth_id, **td.vitality.model_dump()))
        if td.implant:
            session.add(ToothImplant(tooth_id=tooth.tooth_id, **td.implant.model_dump()))
        if td.restorations:
            session.add(ToothRestoration(tooth_id=tooth.tooth_id, **td.restorations.model_dump()))

        # 1-to-many
        for c in td.caries:
            session.add(ToothCaries(tooth_id=tooth.tooth_id, **c.model_dump()))
        for f in td.fillings:
            session.add(ToothFilling(tooth_id=tooth.tooth_id, **f.model_dump()))
        

    session.commit()
    session.refresh(status)
    return _build_response(session, status)


def get_dental_status_by_chart_id(
    session: Session,
    chart_id: uuid.UUID,
) -> DentalStatusResponse | None:

    status = session.exec(
        select(DentalStatus)
        .where(DentalStatus.chart_id == chart_id)
        .order_by(DentalStatus.created_at.desc())
    ).first()

    if not status:
        raise HTTPException(status_code=404, detail="Chart not found")

    return _build_response(session, status)


def delete_dental_status(
    session: Session,
    status_id: uuid.UUID,
) -> None:
    status = session.get(DentalStatus, status_id)
    if status:
        _delete_teeth_for_status(session, status.status_id)
        session.delete(status)
        session.commit()
