from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.authen import require_chart_owner
from app.core.database import get_session
from app.models.profile import Profile
from app.schemas.pdf_export import ChartExportResponse
from app.services.pdf_export import get_chart_export_data

router = APIRouter()


@router.get(
    "",
    response_model=ChartExportResponse,
    status_code=status.HTTP_200_OK,
)
def get_chart_export_data_endpoint(
    chart_id: uuid.UUID,
    session: Session = Depends(get_session),
) -> ChartExportResponse:
    return get_chart_export_data(session, chart_id)
