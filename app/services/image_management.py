from __future__ import annotations

import os
import uuid
from functools import partial
from threading import Lock
from time import monotonic
from typing import Any

from fastapi import HTTPException
from sqlmodel import Session, select
from app.core.supabase import get_supabase

from app.models.image_management import ImageManagement, ImageManagementCreate, ImageManagementUpdate


def create_image_management(session: Session, chart_id: uuid.UUID, payload: ImageManagementCreate) -> ImageManagement:
    from app.models.dental_chart import DentalChart

    if not chart_id or not session.get(DentalChart, chart_id):
        raise HTTPException(status_code=404, detail="Dental chart not found")

    # file_size is upload metadata validated on the Create schema; it is not
    # a column on image_management.
    item = ImageManagement.model_validate(
        {**payload.model_dump(exclude={"file_size"}), "chart_id": chart_id}
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_image_management_by_id(session: Session, image_id: uuid.UUID) -> ImageManagement | None:
    item = session.get(ImageManagement, image_id)
    if not item:
        raise HTTPException(status_code=404, detail="Image not found")
    return item

def update_image_management(
    session: Session,
    image_id: uuid.UUID,
    payload: ImageManagementUpdate,
) -> ImageManagement:
    item = get_image_management_by_id(session, image_id)

    updates = payload.model_dump(exclude_unset=True,exclude_none=True)
    for key, value in updates.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_image_management(session: Session, image_id: uuid.UUID) -> None:
    item = get_image_management_by_id(session, image_id)

    # ai_detection_analysis.image_id has no ON DELETE CASCADE (no migration
    # system for this project's existing tables) — clear dependent AI results
    # first, or the FK constraint blocks the delete.
    from app.models.ai_detection_analysis import AIDetectionAnalysis

    dependent_analyses = session.exec(
        select(AIDetectionAnalysis).where(AIDetectionAnalysis.image_id == image_id)
    ).all()
    for analysis in dependent_analyses:
        session.delete(analysis)

    session.delete(item)
    session.commit()


EXPIRES_IN = 86400
SIGNED_URL_CACHE_TTL = EXPIRES_IN - 300
_signed_url_cache: dict[str, tuple[float, str]] = {}
_signed_url_cache_lock = Lock()

def get_signed_url(image_path: str, force_refresh: bool = False) -> str:
    now = monotonic()
    with _signed_url_cache_lock:
        cached = _signed_url_cache.get(image_path)
        if not force_refresh and cached and now - cached[0] < SIGNED_URL_CACHE_TTL:
            return cached[1]

    SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")
    supabase = get_supabase()
    result = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(
        image_path, EXPIRES_IN
    )
    if not result or "signedURL" not in result:
        raise Exception(f"Failed to generate signed URL for {image_path}")
    signed_url = result["signedURL"]
    with _signed_url_cache_lock:
        _signed_url_cache[image_path] = (now, signed_url)
    return signed_url

from concurrent.futures import ThreadPoolExecutor
def get_all_image_management_signed(
    session: Session,
    chart_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    force_refresh: bool = False,
) -> list[dict[str, Any]]:
    statement = select(ImageManagement).where(ImageManagement.chart_id == chart_id).offset(skip).limit(limit)
    items = list(session.exec(statement).all())
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        if force_refresh:
            result = list(executor.map(partial(enrich_item, force_refresh=True), items))
        else:
            result = list(executor.map(enrich_item, items))
        
    return result


def get_all_patient_image_management_signed(
    session: Session,
    patient_id: uuid.UUID,
    force_refresh: bool = False,
) -> list[dict[str, Any]]:
    from app.models.dental_chart import DentalChart

    items = list(session.exec(
        select(ImageManagement)
        .join(DentalChart, ImageManagement.chart_id == DentalChart.chart_id)
        .where(DentalChart.patient_id == patient_id)
        .order_by(ImageManagement.uploaded_at.desc())
    ).all())
    with ThreadPoolExecutor(max_workers=5) as executor:
        return list(executor.map(partial(enrich_item, force_refresh=force_refresh), items))

# Parallelize the enrichment of items to generate signed URLs faster
def enrich_item(item: ImageManagement, force_refresh: bool = False) -> dict[str, Any]:
    item_dict = item.model_dump()
    image_type = item.image_type.value if hasattr(item.image_type, 'value') else item.image_type
    path = f"{image_type}/{item.image_file}"
    if force_refresh:
        item_dict["image_url"] = get_signed_url(path, force_refresh=True)
    else:
        item_dict["image_url"] = get_signed_url(path)
    return item_dict