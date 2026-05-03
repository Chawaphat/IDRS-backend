import uuid
from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel

from app.models.enums import CariesType, SurfaceEnum


class ToothSurfacePayload(SQLModel):
    surface: SurfaceEnum
    condition: CariesType


class ToothPayload(SQLModel):
    tooth_number: int
    tooth_status: str | None = None
    tooth_detail: str | None = None
    crown: str | None = None
    root_status: str | None = None
    surfaces: list[ToothSurfacePayload] = []


class DentalStatusBulkCreate(SQLModel):
    teeth: list[ToothPayload]
    
    
class ToothSurfaceResponse(SQLModel):
    surface_id: uuid.UUID
    surface: SurfaceEnum
    condition: CariesType


class ToothResponse(SQLModel):
    tooth_id: uuid.UUID
    tooth_number: int
    tooth_status: Optional[str] = None
    tooth_detail: Optional[str] = None
    crown: Optional[str] = None
    root_status: Optional[str] = None
    surfaces: List[ToothSurfaceResponse]


class DentalStatusResponse(SQLModel):
    status_id: uuid.UUID
    chart_id: uuid.UUID
    created_at: datetime
    teeth: List[ToothResponse]