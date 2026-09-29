from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import TypeVar

from fastapi import HTTPException
from sqlmodel import Session

from app.models.dental_chart import DentalChart
from app.models.esthetic_evaluation import EstheticEvaluation
from app.models.extraoral_exam import ExtraoralExam
from app.models.medical_histories import MedicalHistory
from app.models.occlusal_analysis import OcclusalAnalysis
from app.models.profile import Profile
from app.models.residual_ridge_assessment import ResidualRidgeAssessment
from app.models.vdo_evaluation import VdoEvaluation
from app.schemas.dental_status import DentalStatusResponse
from app.schemas.pdf_export import ChartExportResponse
from app.services.dental_chart import get_dental_chart_by_id
from app.services.dental_status import get_dental_status_by_chart_id
from app.services.esthetic_evaluation import get_esthetic_evaluation_by_chart_id
from app.services.extraoral_exam import get_extraoral_exam_by_chart_id
from app.services.image_management import get_all_image_management_signed
from app.services.medical_histories import get_medical_history_by_chart_id
from app.services.occlusal_analysis import get_occlusal_analysis_by_chart_id
from app.services.occlusal_contact import get_occlusal_contacts_by_chart_id
from app.services.patient import get_patient_by_id
from app.services.residual_ridge_assessment import get_residual_ridge_assessment_by_chart_id
from app.services.vdo_evaluation import get_vdo_evaluation_by_chart_id

T = TypeVar("T")


def _optional_section(loader: Callable[[], T]) -> T | None:
    try:
        return loader()
    except HTTPException as exc:
        if exc.status_code == 404:
            return None
        raise


# def _authorize_chart_export(chart: DentalChart, current_user: Profile) -> None:
#     if current_user.role == "dentist" and chart.dentist_id != current_user.id:
#         raise HTTPException(
#             status_code=403,
#             detail="Not authorized. You are not the owner of this chart.",
#         )


def get_chart_export_data(
    session: Session,
    chart_id: uuid.UUID,
) -> ChartExportResponse:
    chart = get_dental_chart_by_id(session, chart_id)
    # _authorize_chart_export(chart, current_user)

    patient = get_patient_by_id(session, chart.patient_id, chart.dentist_id)

    medical_history: MedicalHistory | None = _optional_section(
        lambda: get_medical_history_by_chart_id(session, chart_id)
    )
    extraoral_exam: ExtraoralExam | None = _optional_section(
        lambda: get_extraoral_exam_by_chart_id(session, chart_id)
    )
    esthetic_evaluation: EstheticEvaluation | None = _optional_section(
        lambda: get_esthetic_evaluation_by_chart_id(session, chart_id)
    )
    vdo_evaluation: VdoEvaluation | None = _optional_section(
        lambda: get_vdo_evaluation_by_chart_id(session, chart_id)
    )
    residual_ridge_assessment: ResidualRidgeAssessment | None = _optional_section(
        lambda: get_residual_ridge_assessment_by_chart_id(session, chart_id)
    )
    occlusal_analysis: OcclusalAnalysis | None = _optional_section(
        lambda: get_occlusal_analysis_by_chart_id(session, chart_id)
    )
    dental_status: DentalStatusResponse | None = _optional_section(
        lambda: get_dental_status_by_chart_id(session, chart_id)
    )

    return ChartExportResponse(
        patient=patient,
        chart=chart,
        medical_history=medical_history,
        extraoral_exam=extraoral_exam,
        esthetic_evaluation=esthetic_evaluation,
        vdo_evaluation=vdo_evaluation,
        residual_ridge_assessment=residual_ridge_assessment,
        occlusal_analysis=occlusal_analysis,
        occlusal_contacts=get_occlusal_contacts_by_chart_id(session, chart_id),
        images=get_all_image_management_signed(session, chart_id),
        dental_status=dental_status,
    )
