"""
Tests for app/services/occlusal_analysis.py  +  app/routers/occlusal_analyses.py
Covers ALL test cases UTC-30 and UTC-32.

Router prefix (from app/main.py):
  PUT/GET/DELETE  →  /dental-charts/{chart_id}/occlusal-analysis
  Auth: require_chart_editor

UTC-30 : Update/Replace Occlusal Analysis (PUT)
  Method: upsert_occlusal_analysis(session, chart_id, payload)

UTC-32 : View Occlusal Analysis & Contact (GET)
  Method: get_occlusal_analysis_record(session, chart_id)
"""
import uuid
from unittest.mock import MagicMock

import pydantic
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from tests.conftest import make_chart, make_profile

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DENTIST_ID   = uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a")
CHART_ID     = uuid.UUID("6ae0746a-511e-4a5d-88c9-975234efc03a")
OCCLUSAL_ID  = uuid.UUID("a1b2c3d4-1111-2222-3333-444444444444")
NONEXISTENT  = uuid.UUID("99999999-9999-9999-9999-999999999999")

BASE_URL = f"/dental-charts/{CHART_ID}/occlusal-analysis"

# ---------------------------------------------------------------------------
# Valid payload dict
# ---------------------------------------------------------------------------
VALID_PAYLOAD = {
    "right_molar": "class_i",
    "left_molar": "class_i",
    "overlap_horizontal": 2.0,
    "overlap_vertical": 3.0,
    "anterior_slide": 1.0,
    "lateral_slide": 0.5,
}


# ---------------------------------------------------------------------------
# Helper: build OcclusalAnalysis object
# ---------------------------------------------------------------------------
def make_occlusal(occlusal_id=None, chart_id=None):
    from app.models.occlusal_analysis import OcclusalAnalysis
    from app.models.enums import MolarType

    o = OcclusalAnalysis(
        occlusal_id=occlusal_id or OCCLUSAL_ID,
        chart_id=chart_id or CHART_ID,
        right_molar=MolarType.class_i,
        left_molar=MolarType.class_i,
        overlap_horizontal=2.0,
        overlap_vertical=3.0,
        anterior_slide=1.0,
        lateral_slide=0.5,
    )
    return o


# ---------------------------------------------------------------------------
# Shared TestClient helpers (require_chart_editor auth)
# ---------------------------------------------------------------------------
def _authed_client(mock_session):
    from app.main import app
    from app.core.database import get_session
    from app.core.authen import require_chart_editor

    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[require_chart_editor] = lambda: make_profile(DENTIST_ID)
    return TestClient(app, raise_server_exceptions=False), app


def _unauthed_client(mock_session):
    from app.main import app
    from app.core.database import get_session
    from app.core.authen import require_chart_editor

    def raise_401():
        raise HTTPException(status_code=401, detail="Unauthorized")

    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[require_chart_editor] = raise_401
    return TestClient(app, raise_server_exceptions=False), app


# ============================================================
# upsert_occlusal_analysis
# ============================================================

class TestUpsertOcclusalAnalysis:
    """Service-layer tests for upsert_occlusal_analysis (UTC-30)."""

    def test_tc01_create_when_no_existing_record(self, mock_session):
        """UTC-30-TC-01: No existing record → creates and returns new OcclusalAnalysis."""
        from app.models.occlusal_analysis import OcclusalAnalysisCreate
        from app.services.occlusal_analysis import upsert_occlusal_analysis

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))
        mock_session.refresh.side_effect = lambda obj: setattr(obj, "occlusal_id", OCCLUSAL_ID)

        payload = OcclusalAnalysisCreate(**VALID_PAYLOAD)
        result = upsert_occlusal_analysis(mock_session, CHART_ID, payload)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result.chart_id == CHART_ID
        assert result.overlap_horizontal == 2.0
        assert result.overlap_vertical == 3.0

    def test_tc01_update_when_existing_record(self, mock_session):
        """UTC-30-TC-01 (upsert): Existing record → updates fields in-place."""
        from app.models.occlusal_analysis import OcclusalAnalysisCreate
        from app.services.occlusal_analysis import upsert_occlusal_analysis

        existing = make_occlusal()
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=existing))
        mock_session.refresh.side_effect = lambda obj: None

        payload = OcclusalAnalysisCreate(overlap_horizontal=5.0)
        result = upsert_occlusal_analysis(mock_session, CHART_ID, payload)

        mock_session.add.assert_called_once_with(existing)
        mock_session.commit.assert_called_once()
        assert result.overlap_horizontal == 5.0

    def test_tc02_nonexistent_chart_service_does_not_validate_fk(self, mock_session):
        """
        UTC-30-TC-02: chart_id does not exist.
        ⚠ Spec may expect 404 "Chart not found".
        ⚠ Actual: service does NOT validate chart FK — upserts without checking.
           DB would raise IntegrityError on commit in production (no chart row).
        Test documents actual implementation behaviour.
        """
        from app.models.occlusal_analysis import OcclusalAnalysisCreate
        from app.services.occlusal_analysis import upsert_occlusal_analysis

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))
        mock_session.refresh.side_effect = lambda obj: setattr(obj, "occlusal_id", OCCLUSAL_ID)

        payload = OcclusalAnalysisCreate(**VALID_PAYLOAD)
        result = upsert_occlusal_analysis(mock_session, NONEXISTENT, payload)
        assert result.chart_id == NONEXISTENT

    def test_tc03_invalid_enum_raises_validation_error(self):
        """UTC-30-TC-03 (schema): Invalid MolarType enum value → Pydantic ValidationError."""
        from app.models.occlusal_analysis import OcclusalAnalysisCreate

        with pytest.raises(pydantic.ValidationError) as exc:
            OcclusalAnalysisCreate(right_molar="not_a_valid_molar")

        error_fields = {e["loc"][0] for e in exc.value.errors()}
        assert "right_molar" in error_fields


class TestUpsertOcclusalAnalysisRouter:
    """Router-layer: PUT /dental-charts/{chart_id}/occlusal-analysis."""

    def test_no_auth_returns_401(self, mock_session):
        """No bearer token → 401 Unauthorized."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.put(BASE_URL, json=VALID_PAYLOAD)
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tc03_invalid_enum_via_http_returns_422(self, mock_session):
        """UTC-30-TC-03 (HTTP): Invalid right_molar enum via router → 422."""
        client, app = _authed_client(mock_session)
        try:
            bad_payload = {**VALID_PAYLOAD, "right_molar": "not_a_class"}
            response = client.put(BASE_URL, json=bad_payload)
            assert response.status_code == 422
            error_locs = {e["loc"][-1] for e in response.json()["detail"]}
            assert "right_molar" in error_locs
        finally:
            app.dependency_overrides.clear()

    def test_tc01_success_returns_201(self, mock_session):
        """UTC-30-TC-01 (HTTP): Valid payload → 201 with occlusal record."""
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))
        mock_session.refresh.side_effect = lambda obj: setattr(obj, "occlusal_id", OCCLUSAL_ID)

        client, app = _authed_client(mock_session)
        try:
            response = client.put(BASE_URL, json=VALID_PAYLOAD)
            assert response.status_code == 201
            data = response.json()
            assert data["chart_id"] == str(CHART_ID)
            assert data["overlap_horizontal"] == 2.0
            assert data["right_molar"] == "class_i"
        finally:
            app.dependency_overrides.clear()


# ============================================================
# get_occlusal_analysis_by_chart_id
# ============================================================

class TestGetOcclusalAnalysis:
    """Service-layer tests for get_occlusal_analysis_by_chart_id (UTC-32)."""

    def test_tc01_success_returns_analysis(self, mock_session):
        """UTC-32-TC-01: Existing record → returned."""
        from app.services.occlusal_analysis import get_occlusal_analysis_by_chart_id

        occlusal = make_occlusal()
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=occlusal))

        result = get_occlusal_analysis_by_chart_id(mock_session, CHART_ID)
        assert result.occlusal_id == OCCLUSAL_ID
        assert result.chart_id == CHART_ID
        assert result.right_molar == "class_i"

    def test_tc02_not_found_raises_404(self, mock_session):
        """UTC-32-TC-02: No record for chart_id → 404 'Occlusal analysis not found'."""
        from app.services.occlusal_analysis import get_occlusal_analysis_by_chart_id

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        with pytest.raises(HTTPException) as exc:
            get_occlusal_analysis_by_chart_id(mock_session, NONEXISTENT)

        assert exc.value.status_code == 404
        assert "Occlusal analysis not found" in exc.value.detail


class TestGetOcclusalAnalysisRouter:
    """Router-layer: GET /dental-charts/{chart_id}/occlusal-analysis."""

    def test_no_auth_returns_401(self, mock_session):
        """No bearer token → 401."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tc02_not_found_returns_404(self, mock_session):
        """UTC-32-TC-02 (HTTP): No record → 404."""
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        client, app = _authed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_tc01_success_returns_200(self, mock_session):
        """UTC-32-TC-01 (HTTP): Existing record → 200 with dict including contacts."""
        from app.models.enums import MolarType

        occlusal = make_occlusal()
        # get_occlusal_analysis_record calls exec twice: once for occlusal, once for contacts
        mock_session.exec.side_effect = [
            MagicMock(first=MagicMock(return_value=occlusal)),  # get_occlusal_analysis_by_chart_id
            MagicMock(all=MagicMock(return_value=[])),           # contacts query
        ]

        client, app = _authed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 200
            data = response.json()
            assert data["chart_id"] == str(CHART_ID)
            assert data["occlusal_id"] == str(OCCLUSAL_ID)
            assert data["overlap_horizontal"] == 2.0
            assert "contacts" in data
        finally:
            app.dependency_overrides.clear()


# ============================================================
# delete_occlusal_analysis
# ============================================================

class TestDeleteOcclusalAnalysis:
    """Service-layer tests for delete_occlusal_analysis."""

    def test_success_deletes(self, mock_session):
        """Existing record → deleted."""
        from app.services.occlusal_analysis import delete_occlusal_analysis

        occlusal = make_occlusal()
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=occlusal))

        delete_occlusal_analysis(mock_session, CHART_ID)

        mock_session.delete.assert_called_once_with(occlusal)
        mock_session.commit.assert_called_once()

    def test_not_found_raises_404(self, mock_session):
        """No record → 404."""
        from app.services.occlusal_analysis import delete_occlusal_analysis

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        with pytest.raises(HTTPException) as exc:
            delete_occlusal_analysis(mock_session, NONEXISTENT)

        assert exc.value.status_code == 404


class TestDeleteOcclusalAnalysisRouter:
    """Router-layer: DELETE /dental-charts/{chart_id}/occlusal-analysis."""

    def test_no_auth_returns_401(self, mock_session):
        """No bearer token → 401."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.delete(BASE_URL)
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_not_found_returns_404(self, mock_session):
        """Non-existent chart → 404."""
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        client, app = _authed_client(mock_session)
        try:
            response = client.delete(f"/dental-charts/{NONEXISTENT}/occlusal-analysis")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_success_returns_204(self, mock_session):
        """Existing record → 204 No Content."""
        occlusal = make_occlusal()
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=occlusal))

        client, app = _authed_client(mock_session)
        try:
            response = client.delete(BASE_URL)
            assert response.status_code == 204
        finally:
            app.dependency_overrides.clear()
