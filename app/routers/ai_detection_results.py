from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.ai_detection_result import (
    create_ai_detection_result,
    delete_ai_detection_result,
    get_ai_detection_result_by_id,
    get_ai_detection_result_by_image_id,
    get_all_ai_detection_results,
    update_ai_detection_result,
)
from app.models.ai_detection_result import (
    AIDetectionResult,
    AIDetectionResultCreate,
    AIDetectionResultUpdate,
)

router = APIRouter()


@router.post("", response_model=AIDetectionResult, status_code=status.HTTP_201_CREATED)
def create_ai_detection_result_endpoint(
    payload: AIDetectionResultCreate,
    session: Session = Depends(get_session),
) -> AIDetectionResult:
    return create_ai_detection_result(session, payload)


@router.get("", response_model=list[AIDetectionResult])
def get_ai_detection_results_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[AIDetectionResult]:
    return get_all_ai_detection_results(session, skip=skip, limit=limit)


@router.get("/{result_id}", response_model=AIDetectionResult)
def get_ai_detection_result_by_id_endpoint(
    result_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> AIDetectionResult:
    item = get_ai_detection_result_by_id(session, result_id)
    if item is None:
        raise HTTPException(status_code=404, detail="AI detection result not found")
    return item

@router.get("/by-image/{image_id}", response_model=AIDetectionResult)
def get_ai_detection_result_by_image_id_endpoint(
    image_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> AIDetectionResult:
    item = get_ai_detection_result_by_image_id(session, image_id)
    if item is None:
        raise HTTPException(status_code=404, detail="AI detection result not found")
    return item


@router.put("/{result_id}", response_model=AIDetectionResult)
def update_ai_detection_result_endpoint(
    result_id: uuid.UUID,
    payload: AIDetectionResultUpdate,
    session: Session = Depends(get_session),
) -> AIDetectionResult:
    item = get_ai_detection_result_by_id(session, result_id)
    if item is None:
        raise HTTPException(status_code=404, detail="AI detection result not found")
    return update_ai_detection_result(session, item, payload)


@router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ai_detection_result_endpoint(
    result_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    item = get_ai_detection_result_by_id(session, result_id)
    if item is None:
        raise HTTPException(status_code=404, detail="AI detection result not found")
    delete_ai_detection_result(session, item)
