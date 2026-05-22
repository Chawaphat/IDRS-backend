from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.enums import (
    ToothTypeEnum, EdentulousTypeEnum,
    CariesDepthEnum, ToothSurfaceEnum, FillingMaterialEnum,
    MobilityGradeEnum, EptResultEnum, RootCanalTreatedEnum,
    RestorationTypeEnum, RestorationMaterialEnum, PostTypeEnum,
    ImplantComponentEnum, RetentionTypeEnum,
)

# ─────────────────────────────────────────
# PAYLOADS (Frontend → Backend)
# ─────────────────────────────────────────

class EdentulousPayload(BaseModel):
    edentulous_type: EdentulousTypeEnum
    note: Optional[str] = None

class CariesPayload(BaseModel):
    surface: ToothSurfaceEnum
    depth: CariesDepthEnum
    note: Optional[str] = None

class FillingPayload(BaseModel):
    surfaces: list[ToothSurfaceEnum]   
    material: FillingMaterialEnum
    size_mm: Optional[float] = None
    note: Optional[str] = None

class PeriodontalPayload(BaseModel):
    mobility_grade: Optional[MobilityGradeEnum] = None
    recession_mm: Optional[float] = None
    note: Optional[str] = None

class VitalityPayload(BaseModel):
    pulp_status: Optional[str] = None
    ept_result: Optional[EptResultEnum] = None
    root_canal_treated: Optional[RootCanalTreatedEnum] = None
    note: Optional[str] = None

class RestorationPayload(BaseModel):
    restoration_type: RestorationTypeEnum
    material: Optional[RestorationMaterialEnum] = None
    post_type: Optional[PostTypeEnum] = None
    note: Optional[str] = None

class ImplantPayload(BaseModel):
    component_type: ImplantComponentEnum
    retention_type: Optional[RetentionTypeEnum] = None
    material: Optional[RestorationMaterialEnum] = None
    brand: Optional[str] = None
    crown_brand: Optional[str] = None
    note: Optional[str] = None

class ToothPayload(BaseModel):
    tooth_number: int
    tooth_type: ToothTypeEnum
    note: Optional[str] = None

    # sub-findings (optional ทั้งหมด)
    edentulous: Optional[EdentulousPayload] = None
    caries: list[CariesPayload] = []
    fillings: list[FillingPayload] = []
    periodontal: Optional[PeriodontalPayload] = None
    vitality: Optional[VitalityPayload] = None
    restorations: Optional[RestorationPayload] = None
    implant: Optional[ImplantPayload] = None

class DentalStatusBulkCreate(BaseModel):
    teeth: list[ToothPayload]


# ─────────────────────────────────────────
# RESPONSES (Backend → Frontend)
# ─────────────────────────────────────────

class EdentulousResponse(BaseModel):
    edentulous_id: uuid.UUID
    edentulous_type: EdentulousTypeEnum
    note: Optional[str] = None

class CariesResponse(BaseModel):
    caries_id: uuid.UUID
    surface: ToothSurfaceEnum
    depth: CariesDepthEnum
    note: Optional[str] = None

class FillingResponse(BaseModel):
    filling_id: uuid.UUID
    surfaces: list[ToothSurfaceEnum]
    material: FillingMaterialEnum
    size_mm: Optional[float] = None
    note: Optional[str] = None

class PeriodontalResponse(BaseModel):
    periodontal_id: uuid.UUID
    mobility_grade: Optional[MobilityGradeEnum] = None
    recession_mm: Optional[float] = None
    note: Optional[str] = None

class VitalityResponse(BaseModel):
    vitality_id: uuid.UUID
    pulp_status: Optional[str] = None
    ept_result: Optional[EptResultEnum] = None
    root_canal_treated: Optional[RootCanalTreatedEnum] = None
    note: Optional[str] = None

class RestorationResponse(BaseModel):
    restoration_id: uuid.UUID
    restoration_type: RestorationTypeEnum
    material: Optional[RestorationMaterialEnum] = None
    post_type: Optional[PostTypeEnum] = None
    note: Optional[str] = None

class ImplantResponse(BaseModel):
    implant_id: uuid.UUID
    component_type: ImplantComponentEnum
    retention_type: Optional[RetentionTypeEnum] = None
    material: Optional[RestorationMaterialEnum] = None
    brand: Optional[str] = None
    crown_brand: Optional[str] = None
    note: Optional[str] = None

class ToothResponse(BaseModel):
    tooth_id: uuid.UUID
    tooth_number: int
    tooth_type: ToothTypeEnum
    note: Optional[str] = None

    edentulous: Optional[EdentulousResponse] = None
    caries: list[CariesResponse] = []
    fillings: list[FillingResponse] = []
    periodontal: Optional[PeriodontalResponse] = None
    vitality: Optional[VitalityResponse] = None
    restorations: Optional[RestorationResponse] = None
    implant: Optional[ImplantResponse] = None

class DentalStatusResponse(BaseModel):
    status_id: uuid.UUID
    chart_id: uuid.UUID
    created_at: datetime
    teeth: list[ToothResponse]