import uuid
from datetime import datetime

import pytest
from fastapi import HTTPException

from tests.conftest import make_chart, make_patient


DENTIST_ID = uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a")
PATIENT_ID = uuid.UUID("3fb0f7b1-da69-4793-a7c7-a6f441dd2f23")
CHART_ID = uuid.UUID("d8454cab-1a71-46e8-8ac1-69ebae557d5a")
IMAGE_ID = uuid.UUID("6e8d89e9-0975-42fc-85df-afb697568ee8")


def make_image(image_id=IMAGE_ID, chart_id=CHART_ID):
    from app.models.enums import ImageCategory
    from app.models.image_management import ImageManagement

    return ImageManagement(
        image_id=image_id,
        chart_id=chart_id,
        image_type=ImageCategory.intraoral,
        image_url="https://example.test/signed/intraoral/photo.jpg",
        image_file="photo.jpg",
        description="Intraoral photo",
        uploaded_at=datetime.utcnow(),
    )


def _patch_optional_sections_to_missing(pdf_export, monkeypatch):
    def raise_404(session, chart_id):
        raise HTTPException(status_code=404, detail="Section not found")

    monkeypatch.setattr(pdf_export, "get_medical_history_by_chart_id", raise_404)
    monkeypatch.setattr(pdf_export, "get_extraoral_exam_by_chart_id", raise_404)
    monkeypatch.setattr(pdf_export, "get_esthetic_evaluation_by_chart_id", raise_404)
    monkeypatch.setattr(pdf_export, "get_vdo_evaluation_by_chart_id", raise_404)
    monkeypatch.setattr(pdf_export, "get_residual_ridge_assessment_by_chart_id", raise_404)
    monkeypatch.setattr(pdf_export, "get_occlusal_analysis_by_chart_id", raise_404)
    monkeypatch.setattr(pdf_export, "get_dental_status_by_chart_id", raise_404)


class TestGetChartExportData:
    def test_success_returns_chart_patient_images_and_optional_empty_sections(
        self,
        mock_session,
        monkeypatch,
    ):
        from app.services import pdf_export

        chart = make_chart(chart_id=CHART_ID, patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        image = make_image()

        monkeypatch.setattr(pdf_export, "get_dental_chart_by_id", lambda session, chart_id: chart)
        monkeypatch.setattr(
            pdf_export,
            "get_patient_by_id",
            lambda session, patient_id, dentist_id: patient,
        )
        monkeypatch.setattr(pdf_export, "get_occlusal_contacts_by_chart_id", lambda session, chart_id: [])
        monkeypatch.setattr(pdf_export, "get_all_image_management_signed", lambda session, chart_id: [image])
        _patch_optional_sections_to_missing(pdf_export, monkeypatch)

        result = pdf_export.get_chart_export_data(mock_session, CHART_ID)

        assert result.chart.chart_id == CHART_ID
        assert result.patient.patient_id == PATIENT_ID
        assert result.medical_history is None
        assert result.extraoral_exam is None
        assert result.esthetic_evaluation is None
        assert result.vdo_evaluation is None
        assert result.residual_ridge_assessment is None
        assert result.occlusal_analysis is None
        assert result.occlusal_contacts == []
        assert result.dental_status is None
        assert len(result.images) == 1
        assert result.images[0].image_id == IMAGE_ID
        assert result.images[0].image_url == "https://example.test/signed/intraoral/photo.jpg"

    def test_chart_not_found_propagates_404_and_skips_other_loaders(self, mock_session, monkeypatch):
        from app.services import pdf_export

        def raise_chart_404(session, chart_id):
            raise HTTPException(status_code=404, detail="Dental chart not found")

        monkeypatch.setattr(pdf_export, "get_dental_chart_by_id", raise_chart_404)

        called = {"patient": False}

        def get_patient(*args, **kwargs):
            called["patient"] = True

        monkeypatch.setattr(pdf_export, "get_patient_by_id", get_patient)

        with pytest.raises(HTTPException) as exc:
            pdf_export.get_chart_export_data(mock_session, CHART_ID)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Dental chart not found"
        assert called["patient"] is False

    def test_optional_non_404_error_is_not_swallowed(self, mock_session, monkeypatch):
        from app.services import pdf_export

        chart = make_chart(chart_id=CHART_ID, patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID)

        monkeypatch.setattr(pdf_export, "get_dental_chart_by_id", lambda session, chart_id: chart)
        monkeypatch.setattr(
            pdf_export,
            "get_patient_by_id",
            lambda session, patient_id, dentist_id: patient,
        )

        def raise_500(session, chart_id):
            raise HTTPException(status_code=500, detail="Database unavailable")

        monkeypatch.setattr(pdf_export, "get_medical_history_by_chart_id", raise_500)

        with pytest.raises(HTTPException) as exc:
            pdf_export.get_chart_export_data(mock_session, CHART_ID)

        assert exc.value.status_code == 500
        assert exc.value.detail == "Database unavailable"


class TestChartExportRouter:
    def test_export_route_returns_200_with_images(self, mock_session, monkeypatch):
        from app.core.authen import require_chart_owner
        from app.core.database import get_session
        from app.main import app
        from app.routers import pdf_export as pdf_export_router
        from app.schemas.pdf_export import ChartExportResponse
        from fastapi.testclient import TestClient

        chart = make_chart(chart_id=CHART_ID, patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        image = make_image()

        monkeypatch.setattr(
            pdf_export_router,
            "get_chart_export_data",
            lambda session, chart_id: ChartExportResponse(
                patient=patient,
                chart=chart,
                occlusal_contacts=[],
                images=[image],
            ),
        )

        app.dependency_overrides[get_session] = lambda: mock_session
        app.dependency_overrides[require_chart_owner] = lambda: None
        try:
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get(f"/dental-charts/{CHART_ID}/export-data")
        finally:
            app.dependency_overrides.clear()

        body = response.json()
        assert response.status_code == 200
        assert body["chart"]["chart_id"] == str(CHART_ID)
        assert body["patient"]["patient_id"] == str(PATIENT_ID)
        assert body["images"][0]["image_id"] == str(IMAGE_ID)
        assert body["images"][0]["image_url"] == "https://example.test/signed/intraoral/photo.jpg"

    def test_export_route_returns_403_when_chart_owner_dependency_rejects(self, mock_session):
        from app.core.authen import require_chart_owner
        from app.core.database import get_session
        from app.main import app
        from fastapi.testclient import TestClient

        def raise_403():
            raise HTTPException(status_code=403, detail="Not authorized")

        app.dependency_overrides[get_session] = lambda: mock_session
        app.dependency_overrides[require_chart_owner] = raise_403
        try:
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get(f"/dental-charts/{CHART_ID}/export-data")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 403
        assert response.json()["detail"] == "Not authorized"
