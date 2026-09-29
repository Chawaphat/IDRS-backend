from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.dental_chart import DentalChart
from app.models.esthetic_evaluation import EstheticEvaluation
from app.models.extraoral_exam import ExtraoralExam
from app.models.image_management import ImageManagement
from app.models.medical_histories import MedicalHistory
from app.models.occlusal_analysis import OcclusalAnalysis
from app.models.occlusal_contact import OcclusalContact
from app.models.patient import Patient
from app.models.residual_ridge_assessment import ResidualRidgeAssessment
from app.models.vdo_evaluation import VdoEvaluation
from app.schemas.dental_status import DentalStatusResponse


class ChartExportResponse(BaseModel):
    patient: Patient
    chart: DentalChart
    medical_history: MedicalHistory | None = None
    extraoral_exam: ExtraoralExam | None = None
    esthetic_evaluation: EstheticEvaluation | None = None
    vdo_evaluation: VdoEvaluation | None = None
    residual_ridge_assessment: ResidualRidgeAssessment | None = None
    occlusal_analysis: OcclusalAnalysis | None = None
    occlusal_contacts: list[OcclusalContact] = Field(default_factory=list)
    images: list[ImageManagement] = Field(default_factory=list)
    dental_status: DentalStatusResponse | None = None
