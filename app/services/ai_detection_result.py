from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.ai_detection_analysis import AIDetectionAnalysis, AIDetectionAnalysisCreate
from app.models.ai_detection_result import AIDetectionResult
from app.models.enums import ImageCategory
from app.models.image_management import ImageManagement
from app.services import ai_inference


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

    predictions = ai_inference.predict(image.image_url)

    analysis = AIDetectionAnalysis(
        image_id=image_id,
        model_name=payload.model_name or ai_inference.MODEL_NAME,
        model_version=payload.model_version or ai_inference.MODEL_VERSION,
    )
    session.add(analysis)
    session.flush()

    # 3. Persist each per-tooth detection, linked to the analysis
    for prediction in predictions:
        result = AIDetectionResult(
            analysis_id=analysis.analysis_id,
            tooth_number=prediction.tooth_number,
            condition=prediction.condition,
            confidence=prediction.confidence,
            bbox=prediction.bbox,
        )
        session.add(result)

    session.commit()
    session.refresh(analysis)
    return analysis


def get_ai_detection_analyses_by_chart_id(
    session: Session,
    chart_id: uuid.UUID,
) -> list[AIDetectionAnalysis]:

    statement = (
        select(AIDetectionAnalysis)
        .join(ImageManagement, AIDetectionAnalysis.image_id == ImageManagement.image_id)
        .where(ImageManagement.chart_id == chart_id)
    )
    return list(session.exec(statement).all())
