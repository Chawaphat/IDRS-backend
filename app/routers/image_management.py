from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.services.image_management import (
    create_image_management,
    delete_image_management,
    get_all_image_management_signed,
    update_image_management,
)
from app.models.image_management import ImageManagement, ImageManagementCreate, ImageManagementUpdate

router = APIRouter()

@router.post("", response_model=ImageManagement, status_code=status.HTTP_201_CREATED)
def create_image_management_endpoint(
    chart_id: uuid.UUID,
    payload: ImageManagementCreate,
    session: Session = Depends(get_session),
) -> ImageManagement:
    try:
        return create_image_management(session, chart_id, payload)
    except HTTPException:
        raise  # let the service's own 404 (missing chart) etc. through unchanged
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[ImageManagement])
def get_image_management_signed_endpoint(
    chart_id: uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[ImageManagement]:
    try:
        return get_all_image_management_signed(session, chart_id=chart_id, skip=skip, limit=limit)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{image_id}", response_model=ImageManagement)
def update_image_management_endpoint(
    image_id: uuid.UUID,
    payload: ImageManagementUpdate,
    session: Session = Depends(get_session),
) -> ImageManagement:
    return update_image_management(session, image_id, payload)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image_management_endpoint(
    image_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> None:
    return delete_image_management(session, image_id)


