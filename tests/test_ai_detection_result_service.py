"""
Tests for app/services/ai_detection_result.py

Covers the backend (FastAPI/Python) unit test cases from
IDRS_Test Plan_V.0.2.0 — Chapter 3.2 "AI Detection Results Module":

  UTC-41 : Run AI Detection on Panoramic X-ray -> create_ai_detection_result()
  UTC-42 : View AI Detection Results           -> get_ai_detection_analyses_by_chart_id()

Layer: service-layer only — the DB Session is a MagicMock and
`ai_inference.predict` is patched (the ML model is never invoked).

"""
import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.ai_detection_analysis import AIDetectionAnalysis, AIDetectionAnalysisCreate
from app.models.enums import ImageCategory
from app.models.image_management import ImageManagement
from app.services import ai_detection_result as svc


# ---------------------------------------------------------------------------
# Constants (match UTC-41 / UTC-42 in the Test Plan)
# ---------------------------------------------------------------------------
CHART_ID = uuid.UUID("8052cd7e-6ae8-4b11-8288-6dc29f9d517a")
IMAGE_ID = uuid.UUID("005599f7-cf0a-4db5-9e2e-1fe71f93a339")
NONEXISTENT_IMAGE_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")
NONEXISTENT_CHART_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")

MODEL_NAME = "DentexSegAndDet"
MODEL_VERSION = "v1.0"

RAW_OUTPUT = {
    "image_size": [2800, 1316],
    "detections": [{"tooth_fdi": 38, "condition": "Impacted", "confidence": 0.91}],
    "teeth": [{"tooth_fdi": 11, "is_healthy": True}],
}


def make_image(image_id=IMAGE_ID, chart_id=CHART_ID,
               image_type=ImageCategory.panoramic_xray,
               image_url="https://signed.url/panoramic_xray/abc.jpg",
               image_file="abc.jpg"):
    return ImageManagement(
        image_id=image_id,
        chart_id=chart_id,
        image_type=image_type,
        image_url=image_url,
        image_file=image_file,
    )


def make_payload():
    return AIDetectionAnalysisCreate(
        image_id=IMAGE_ID,
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
    )


# ===========================================================================
# UTC-41 : Run AI Detection on Panoramic X-ray
# ===========================================================================
class TestRunAIDetection:

    def test_utc_41_tc_01_success_on_panoramic_xray(self, mock_session, monkeypatch):
        """Success: runs the model on an existing panoramic X-ray and stores raw output."""
        image = make_image()
        mock_session.get.return_value = image

        predict = MagicMock(return_value=MagicMock(raw=RAW_OUTPUT))
        monkeypatch.setattr(svc.ai_inference, "predict", predict)

        result = svc.create_ai_detection_result(mock_session, IMAGE_ID, make_payload())

        predict.assert_called_once_with(image.image_url)
        assert isinstance(result, AIDetectionAnalysis)
        assert result.image_id == IMAGE_ID
        assert result.detection_data == RAW_OUTPUT
        assert result.model_name == MODEL_NAME
        assert result.model_version == MODEL_VERSION
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_utc_41_tc_02_image_does_not_exist(self, mock_session, monkeypatch):
        """Failure: image_id does not exist -> HTTPException(404); model not invoked."""
        mock_session.get.return_value = None
        predict = MagicMock()
        monkeypatch.setattr(svc.ai_inference, "predict", predict)

        with pytest.raises(HTTPException) as exc:
            svc.create_ai_detection_result(mock_session, NONEXISTENT_IMAGE_ID, make_payload())

        assert exc.value.status_code == 404
        assert exc.value.detail == "Image not found"
        predict.assert_not_called()
        mock_session.commit.assert_not_called()

    def test_utc_41_tc_03_image_is_not_panoramic_xray(self, mock_session, monkeypatch):
        """Failure: image exists but is not a panoramic X-ray -> HTTPException(400)."""
        mock_session.get.return_value = make_image(image_type=ImageCategory.intraoral)
        predict = MagicMock()
        monkeypatch.setattr(svc.ai_inference, "predict", predict)

        with pytest.raises(HTTPException) as exc:
            svc.create_ai_detection_result(mock_session, IMAGE_ID, make_payload())

        assert exc.value.status_code == 400
        assert exc.value.detail == "Image must be a panoramic X-ray"
        predict.assert_not_called()
        mock_session.commit.assert_not_called()


# ===========================================================================
# UTC-42 : View AI Detection Results
# ===========================================================================
class TestViewAIDetectionResults:

    def test_utc_42_tc_01_chart_has_analysis_records(self, mock_session):
        """Success: chart has associated AI detection analysis records."""
        records = [MagicMock(name="analysis-1"), MagicMock(name="analysis-2")]
        mock_session.exec.return_value.all.return_value = records

        result = svc.get_ai_detection_analyses_by_chart_id(mock_session, CHART_ID)

        assert result == records

    def test_utc_42_tc_02_chart_has_no_analysis_records(self, mock_session):
        """Success: chart has images but no AI detection analysis records -> []."""
        mock_session.exec.return_value.all.return_value = []

        result = svc.get_ai_detection_analyses_by_chart_id(mock_session, CHART_ID)

        assert result == []

    def test_utc_42_tc_03_chart_id_does_not_exist(self, mock_session):
        """Failure: chart_id does not exist -> HTTPException(404, 'Chart not found')."""
        mock_session.get.return_value = None  # chart lookup returns None

        with pytest.raises(HTTPException) as exc:
            svc.get_ai_detection_analyses_by_chart_id(mock_session, NONEXISTENT_CHART_ID)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Chart not found"

    def test_utc_42_tc_03_chart_id_missing(self, mock_session):
        """Failure: falsy chart_id -> HTTPException(404, 'Chart not found')."""
        with pytest.raises(HTTPException) as exc:
            svc.get_ai_detection_analyses_by_chart_id(mock_session, None)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Chart not found"
