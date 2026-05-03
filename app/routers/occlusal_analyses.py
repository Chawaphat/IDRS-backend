from __future__ import annotations

from typing import Any
import uuid

from fastapi import APIRouter, Depends, Query , status
from sqlmodel import Session

from app.core.database import get_session
from app.services.occlusal_analysis import (
    delete_occlusal_analysis,
    get_all_occlusal_analyses,
    get_occlusal_analysis_by_id,
    get_occlusal_analysis_record,
    upsert_occlusal_analysis,
)
from app.models.occlusal_analysis import (
    OcclusalAnalysis,
    OcclusalAnalysisCreate,
)

router = APIRouter()
admin_router = APIRouter()

@router.put("", response_model=OcclusalAnalysis, status_code=status.HTTP_201_CREATED)
def upsert_occlusal_analysis_endpoint(
    chart_id: uuid.UUID,
    payload: OcclusalAnalysisCreate,
    session: Session = Depends(get_session),
) -> OcclusalAnalysis:
    return upsert_occlusal_analysis(session, chart_id, payload)

@router.get("", response_model=dict[str, Any])
def get_occlusal_analysis_record_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    result = get_occlusal_analysis_record(session, chart_id)
    return result

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_occlusal_analysis_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    delete_occlusal_analysis(session, chart_id)


@admin_router.get("", response_model=list[OcclusalAnalysis])
def get_occlusal_analyses_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[OcclusalAnalysis]:
    return get_all_occlusal_analyses(session, skip=skip, limit=limit)

@admin_router.get("/{occlusal_id}", response_model=OcclusalAnalysis)
def get_occlusal_analysis_by_id_endpoint(
    occlusal_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> OcclusalAnalysis:
    item = get_occlusal_analysis_by_id(session, occlusal_id)
    return item