"""
Tests for app/routers/ai_analysis.py

Covers the backend (FastAPI/Python) unit test cases from
IDRS_Test Plan_V.0.2.0 — Chapter 3.2 "AI Detection Results Module":

  UTC-44 : Run Standalone AI Detection -> POST /ai-analysis/detect (detect_endpoint)

Layer: router-layer — a FastAPI TestClient with the DB session mocked and
`ai_inference.predict` patched (the ML model is never invoked). This endpoint
takes an uploaded file, runs the pipeline, and returns the raw payload without
persisting anything or requiring a patient/chart.
"""
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_session
from app.core.authen import require_chart_editor
from app.routers import ai_analysis as router_mod


RAW_OUTPUT = {
    "image_size": {"width": 2800, "height": 1316},
    "detections": [
        {"disease": "Impacted", "confidence": 0.91, "bbox": [10, 20, 30, 40], "tooth_fdi": 38}
    ],
    "teeth": [{"tooth_fdi": 11, "bbox": [1, 2, 3, 4], "diseases": [], "is_healthy": True}],
}


@pytest.fixture
def client(mock_session):
    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[require_chart_editor] = lambda: MagicMock(role="dentist")
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


def _jpg(name="pano.jpg", content=b"\xff\xd8\xff\xe0fakejpeg"):
    return {"file": (name, content, "image/jpeg")}


# ===========================================================================
# UTC-44 : Run Standalone AI Detection on an uploaded panoramic X-ray
# ===========================================================================
class TestStandaloneAIDetection:

    def test_utc_44_tc_01_success_returns_raw_payload(self, client, monkeypatch):
        """Success: a valid JPG/PNG/WebP upload runs the pipeline and returns the
        raw detection payload (image_size, detections, teeth); nothing is persisted."""
        predict = MagicMock(return_value=MagicMock(raw=dict(RAW_OUTPUT)))
        monkeypatch.setattr(router_mod.ai_inference, "predict", predict)

        resp = client.post("/ai-analysis/detect", files=_jpg(), data={"conf": "0.25"})

        assert resp.status_code == 200
        body = resp.json()
        assert set(body) == {"image_size", "detections", "teeth"}
        assert "image" not in body  # temp path stripped before returning
        assert body["detections"][0]["tooth_fdi"] == 38
        predict.assert_called_once()

    def test_utc_44_tc_02_reject_unsupported_content_type(self, client, monkeypatch):
        """Failure: a non-image content type -> HTTPException(400); model not invoked."""
        predict = MagicMock()
        monkeypatch.setattr(router_mod.ai_inference, "predict", predict)

        resp = client.post(
            "/ai-analysis/detect",
            files={"file": ("doc.pdf", b"%PDF-1.4", "application/pdf")},
        )

        assert resp.status_code == 400
        assert "JPG, PNG, or WebP" in resp.json()["detail"]
        predict.assert_not_called()

    def test_utc_44_tc_03_reject_empty_file(self, client, monkeypatch):
        """Failure: an empty upload -> HTTPException(400); model not invoked."""
        predict = MagicMock()
        monkeypatch.setattr(router_mod.ai_inference, "predict", predict)

        resp = client.post("/ai-analysis/detect", files=_jpg(content=b""))

        assert resp.status_code == 400
        assert resp.json()["detail"] == "Uploaded file is empty"
        predict.assert_not_called()

    def test_utc_44_tc_04_model_failure_surfaces_as_500(self, client, monkeypatch):
        """Failure: the inference pipeline raises -> HTTPException(500) with a clean
        'AI detection failed: ...' message, and the temp file is still cleaned up."""
        def _boom(*a, **k):
            raise RuntimeError("weights not found")

        monkeypatch.setattr(router_mod.ai_inference, "predict", _boom)

        resp = client.post("/ai-analysis/detect", files=_jpg())

        assert resp.status_code == 500
        assert resp.json()["detail"].startswith("AI detection failed:")
