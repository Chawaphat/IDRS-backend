from __future__ import annotations

import uuid

from sqlmodel import Session, select

from app.models.ai_detection_result import (
    AIDetectionResult,
    AIDetectionResultCreate,
    AIDetectionResultUpdate,
)


def create_ai_detection_result(
    session: Session,
    payload: AIDetectionResultCreate,
) -> AIDetectionResult:
    item = AIDetectionResult.model_validate(payload)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_ai_detection_result_by_id(session: Session, result_id: uuid.UUID) -> AIDetectionResult | None:
    return session.get(AIDetectionResult, result_id)

def get_ai_detection_result_by_image_id(session: Session, image_id: uuid.UUID) -> AIDetectionResult | None:
    statement = select(AIDetectionResult).where(AIDetectionResult.image_id == image_id)
    return session.exec(statement).first()

def get_all_ai_detection_results(
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[AIDetectionResult]:
    statement = select(AIDetectionResult).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_ai_detection_result(
    session: Session,
    item: AIDetectionResult,
    payload: AIDetectionResultUpdate,
) -> AIDetectionResult:
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_ai_detection_result(session: Session, item: AIDetectionResult) -> None:
    session.delete(item)
    session.commit()
