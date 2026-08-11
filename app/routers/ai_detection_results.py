from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.ai_detection_result import (
    create_ai_detection_result,
    get_ai_detection_analyses_by_chart_id,
)
from app.models.ai_detection_analysis import (
    AIDetectionAnalysis,
    AIDetectionAnalysisCreate,
    AIDetectionAnalysisRead,
)

router = APIRouter()


@router.post("", response_model=AIDetectionAnalysis, status_code=status.HTTP_201_CREATED)
def create_ai_detection_result_endpoint(
    payload: AIDetectionAnalysisCreate,
    session: Session = Depends(get_session),
) -> AIDetectionAnalysis:
    return create_ai_detection_result(session, payload.image_id, payload)


@router.get("", response_model=list[AIDetectionAnalysisRead])
def get_ai_detection_results_by_chart_id_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> list[AIDetectionAnalysis]:
    return get_ai_detection_analyses_by_chart_id(session, chart_id)
