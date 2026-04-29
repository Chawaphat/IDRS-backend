from __future__ import annotations

import os
import uuid

from fastapi import HTTPException
from sqlmodel import Session, select
from app.core.supabase import get_supabase

from app.models.image_management import ImageManagement, ImageManagementCreate, ImageManagementUpdate


def create_image_management(session: Session, chart_id: uuid.UUID, payload: ImageManagementCreate) -> ImageManagement:
    item = ImageManagement.model_validate({**payload.model_dump(), "chart_id": chart_id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_image_management_by_id(session: Session, image_id: uuid.UUID) -> ImageManagement | None:
    item = session.get(ImageManagement, image_id)
    if not item:
        raise HTTPException(status_code=404, detail="Image not found")
    return item


def get_all_image_management(session: Session, chart_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[ImageManagement]:
    statement = select(ImageManagement).where(ImageManagement.chart_id == chart_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


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
    session.delete(item)
    session.commit()


EXPIRES_IN = 86400  # 1 Days

def get_signed_url(image_path: str) -> str:
    SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")
    supabase = get_supabase()
    result = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(
        image_path, EXPIRES_IN
    )
    if not result or "signedURL" not in result:
        raise Exception(f"Failed to generate signed URL for {image_path}")
    return result["signedURL"]

from concurrent.futures import ThreadPoolExecutor
def get_all_image_management_signed(session: Session, chart_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[dict]:
    statement = select(ImageManagement).where(ImageManagement.chart_id == chart_id).offset(skip).limit(limit)
    items = list(session.exec(statement).all())
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        result = list(executor.map(enrich_item, items))
        
    return result

# Parallelize the enrichment of items to generate signed URLs faster
def enrich_item(item):
    item_dict = item.model_dump()
    path = f"{item.image_type}/{item.image_file}"
    item_dict["image_url"] = get_signed_url(path)
    return item_dict