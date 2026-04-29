from __future__ import annotations

from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.occlusal_analysis import (
    create_occlusal_analysis,
    delete_occlusal_analysis,
    get_all_occlusal_analyses,
    get_occlusal_analysis_by_id,
    get_occlusal_analysis_record,
    update_occlusal_analysis,
)
from app.models.occlusal_analysis import (
    OcclusalAnalysis,
    OcclusalAnalysisCreate,
    OcclusalAnalysisUpdate,
)

router = APIRouter()
admin_router = APIRouter()

@router.post("", response_model=OcclusalAnalysis, status_code=status.HTTP_201_CREATED)
def create_occlusal_analysis_endpoint(
    chart_id: uuid.UUID,
    payload: OcclusalAnalysisCreate,
    session: Session = Depends(get_session),
) -> OcclusalAnalysis:
    return create_occlusal_analysis(session, chart_id, payload)

@router.get("", response_model=dict[str, Any])
def get_occlusal_analysis_record_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    result = get_occlusal_analysis_record(session, chart_id)
    return result

@router.put("", response_model=dict[str, Any], status_code=status.HTTP_200_OK)
def update_occlusal_analysis_endpoint(
    chart_id: uuid.UUID,
    payload: OcclusalAnalysisUpdate,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    updates= payload.model_dump(exclude_unset=True, exclude_none=True)
    item = update_occlusal_analysis(session, chart_id, payload)
    return {
        "occlusal_id": item.occlusal_id,
        "chart_id": item.chart_id,
        **updates,
    }

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