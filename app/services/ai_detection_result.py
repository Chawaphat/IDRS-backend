from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.ai_detection_analysis import AIDetectionAnalysis, AIDetectionAnalysisCreate
from app.models.enums import ImageCategory
from app.models.image_management import ImageManagement
from app.services import ai_inference
from app.services.image_management import get_signed_url


def create_ai_detection_result(
    session: Session,
    image_id: uuid.UUID,
    payload: AIDetectionAnalysisCreate,
) -> AIDetectionAnalysis:

    image = session.get(ImageManagement, image_id)

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    if image.image_type != ImageCategory.panoramic_xray:
        raise HTTPException(status_code=400, detail="Image must be a panoramic X-ray")

    # image_url may not be set if the record was created with only
    # image_file (storage path) — fall back to a fresh signed URL.
    image_source = image.image_url or get_signed_url(f"{image.image_type.value}/{image.image_file}")

    output = ai_inference.predict(image_source)

    # Everything the model returned (per-finding detections + full per-tooth
    # breakdown incl. healthy teeth) lives in detection_data — there is no
    # separate per-tooth results table.
    analysis = AIDetectionAnalysis(
        image_id=image_id,
        model_name=payload.model_name or ai_inference.MODEL_NAME,
        model_version=payload.model_version or ai_inference.MODEL_VERSION,
        detection_data=output.raw,
    )
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


def get_ai_detection_analyses_by_chart_id(
    session: Session,
    chart_id: uuid.UUID,
) -> list[AIDetectionAnalysis]:

    if not chart_id:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    statement = (
        select(AIDetectionAnalysis)
        .join(ImageManagement, AIDetectionAnalysis.image_id == ImageManagement.image_id)
        .where(ImageManagement.chart_id == chart_id)
    )
    return list(session.exec(statement).all())
