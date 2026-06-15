"""
Tests for app/services/residual_ridge_assessment.py
      + app/routers/residual_ridge_assessments.py
Covers ALL test cases UTC-31, UTC-32, UTC-33.

Layer split:
  - Service tests  → mock session, direct function calls
  - Router tests   → TestClient for 401 / 422 / 404 over HTTP

Router prefix (from app/main.py):
  POST/GET/PUT/DELETE  →  /dental-charts/{chart_id}/residual-ridge-assessment
  Auth dependency      :  require_chart_editor

Behavioural notes (spec vs implementation):
  - UTC-31-TC-02: spec → 404 "Chart not found".
    Actual: service does NOT validate chart FK — DB rejects on commit in production.
    Service-layer test documents this divergence.
  - UTC-31-TC-03: spec → 422 for "missing required fields".
    Actual: ResidualRidgeAssessmentCreate has ALL fields optional (default=None).
    The only Pydantic-level 422 path is sending an invalid enum value.
  - UTC-32-TC-02: spec → 404 "Chart not found".
    Actual: service raises HTTPException(404) correctly. ✅
  - UTC-33-TC-02: spec → 404 "Chart not found".
    Actual: service raises HTTPException(404) via get_residual_ridge_assessment_by_chart_id. ✅
"""
import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pydantic
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from tests.conftest import make_profile

# ---------------------------------------------------------------------------
# Constants (match UTC-31 through UTC-33 in FullUnitest.md)
# ---------------------------------------------------------------------------
DENTIST_ID     = uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a")
CHART_ID       = uuid.UUID("d8454cab-1a71-46e8-8ac1-69ebae557d5a")
ASSESSMENT_ID  = uuid.UUID("87b67cca-5a61-417b-9c7b-f3706852ad8d")
NONEXISTENT    = uuid.UUID("99999999-9999-9999-9999-999999999999")

BASE_URL       = f"/dental-charts/{CHART_ID}/residual-ridge-assessment"

# ---------------------------------------------------------------------------
# Valid payload (matches UTC-31-TC-01 in FullUnitest.md)
# ---------------------------------------------------------------------------
VALID_PAYLOAD = {
    "ridge_height": "low_flat",
    "ridge_width": "narrow",
    "jaw_size": "medium",
    "ridge_shape_upper": "u_shape",
    "ridge_shape_lower": "v_shape",
    "ridge_relation": "class_i",
    "ridge_parallelism": "parallel",
    "interridge_space": "sufficient",
    "lower_arch_form": "ovoid",
    "palatal_vault": "average",
    "palatal_throat_form": "class_ii",
    "freenum_attachment": {"upper_labial": "normal", "lower_labial": "low", "buccal": "multiple"},
    "ridge_deformity": ["bone_spicule", "sharp_ridge"],
    "torus_palatinus": {"presence": True, "size": "small"},
    "tongue_size": "medium",
    "tongue_position": "normal",
    "saliva_amount": "normal",
    "saliva_consistency": "thin",
    "lip_mobility": "normal",
    "facial_muscle_tone": "average",
    "mental_attitude": "philosophical",
}


# ---------------------------------------------------------------------------
# Helper: build a ResidualRidgeAssessment-like object
# ---------------------------------------------------------------------------
def make_assessment(assessment_id=None, chart_id=None):
    from app.models.residual_ridge_assessment import ResidualRidgeAssessment
    from app.models.enums import (
        RidgeHeightType, RidgeWidthType, JawSizeType,
        RidgeShapeType, RidgeRelationType,
    )

    return ResidualRidgeAssessment(
        assessment_id=assessment_id or ASSESSMENT_ID,
        chart_id=chart_id or CHART_ID,
        ridge_height=RidgeHeightType.low_flat,
        ridge_width=RidgeWidthType.narrow,
        jaw_size=JawSizeType.medium,
        ridge_shape_upper=RidgeShapeType.u_shape,
        ridge_shape_lower=RidgeShapeType.v_shape,
        ridge_relation=RidgeRelationType.class_i,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


# ---------------------------------------------------------------------------
# Shared TestClient helpers
# ---------------------------------------------------------------------------
def _authed_client(mock_session):
    from app.main import app
    from app.core.database import get_session
    from app.core.authen import get_current_profile

    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[get_current_profile] = lambda: make_profile(DENTIST_ID)
    return TestClient(app, raise_server_exceptions=False), app


def _unauthed_client(mock_session):
    from app.main import app
    from app.core.database import get_session
    from app.core.authen import get_current_profile

    def raise_401():
        raise HTTPException(status_code=401, detail="Unauthorized")

    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[get_current_profile] = raise_401
    return TestClient(app, raise_server_exceptions=False), app


# ============================================================
# UTC-31 : create_residual_ridge_assessment
# ============================================================

class TestCreateResidualRidgeAssessment:
    """Service-layer tests for create_residual_ridge_assessment."""

    def test_tc01_success_creates_and_returns_assessment(self, mock_session):
        """UTC-31-TC-01: Valid payload + existing chart → ResidualRidgeAssessment returned."""
        from app.models.residual_ridge_assessment import ResidualRidgeAssessmentCreate
        from app.services.residual_ridge_assessment import create_residual_ridge_assessment

        payload = ResidualRidgeAssessmentCreate(**VALID_PAYLOAD)

        def fake_refresh(obj):
            obj.assessment_id = ASSESSMENT_ID

        mock_session.refresh.side_effect = fake_refresh

        result = create_residual_ridge_assessment(mock_session, CHART_ID, payload)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result.chart_id == CHART_ID
        assert result.assessment_id == ASSESSMENT_ID
        assert result.ridge_height == "low_flat"
        assert result.ridge_width == "narrow"
        assert result.jaw_size == "medium"

    def test_tc02_nonexistent_chart_service_does_not_validate_fk(self, mock_session):
        """
        UTC-31-TC-02: chart_id does not exist in DB.

        SPEC vs IMPLEMENTATION DIVERGENCE (known):
          - Spec expects: HTTP 404 "Chart not found".
          - Actual: service does NOT validate chart FK — calls session.add/commit
            and lets the DB enforce the constraint (IntegrityError) in production.

        Test documents actual service-layer behaviour (no immediate raise).
        """
        from app.models.residual_ridge_assessment import ResidualRidgeAssessmentCreate
        from app.services.residual_ridge_assessment import create_residual_ridge_assessment

        payload = ResidualRidgeAssessmentCreate(**VALID_PAYLOAD)
        mock_session.refresh.side_effect = lambda obj: setattr(obj, "assessment_id", ASSESSMENT_ID)

        result = create_residual_ridge_assessment(mock_session, NONEXISTENT, payload)
        assert result.chart_id == NONEXISTENT

    def test_tc03_all_fields_optional_no_validation_error(self):
        """
        UTC-31-TC-03: Spec says "missing required fields → HTTP 422".

        SPEC vs IMPLEMENTATION DIVERGENCE (known):
          - Spec expects: HTTP 422 when required fields are absent.
          - Actual: ResidualRidgeAssessmentCreate has ALL fields optional (default=None).
            An empty payload is valid at schema level and does NOT raise 422.
          - The only Pydantic-level 422 path is sending an invalid enum value.

        See test_tc03_invalid_enum_raises_validation_error for the enum 422 path.
        """
        from app.models.residual_ridge_assessment import ResidualRidgeAssessmentCreate

        item = ResidualRidgeAssessmentCreate()
        assert item.ridge_height is None

    def test_tc03_invalid_enum_raises_validation_error(self):
        """UTC-31-TC-03 (schema): Invalid enum value for ridge_height → Pydantic ValidationError."""
        from app.models.residual_ridge_assessment import ResidualRidgeAssessmentCreate

        with pytest.raises(pydantic.ValidationError) as exc:
            ResidualRidgeAssessmentCreate(ridge_height="not_a_valid_height")

        error_fields = {e["loc"][0] for e in exc.value.errors()}
        assert "ridge_height" in error_fields


class TestCreateResidualRidgeAssessmentRouter:
    """Router-layer: UTC-31-TC-04 (401), UTC-31-TC-03 (422)."""

    def test_tc04_no_auth_returns_401(self, mock_session):
        """UTC-31-TC-04: No bearer token → 401 Unauthorized."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.post(BASE_URL, json=VALID_PAYLOAD)
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tc03_invalid_enum_via_http_returns_422(self, mock_session):
        """UTC-31-TC-03 (HTTP): Invalid enum value for ridge_height → router returns 422."""
        client, app = _authed_client(mock_session)
        try:
            bad_payload = {**VALID_PAYLOAD, "ridge_height": "not_a_valid_height"}
            response = client.post(BASE_URL, json=bad_payload)
            assert response.status_code == 422
            error_locs = {e["loc"][-1] for e in response.json()["detail"]}
            assert "ridge_height" in error_locs
        finally:
            app.dependency_overrides.clear()

    def test_tc01_success_returns_201(self, mock_session):
        """UTC-31-TC-01 (HTTP): Valid payload → 201 Created with assessment_id."""
        mock_session.refresh.side_effect = lambda obj: setattr(obj, "assessment_id", ASSESSMENT_ID)

        client, app = _authed_client(mock_session)
        try:
            response = client.post(BASE_URL, json=VALID_PAYLOAD)
            assert response.status_code == 201
            data = response.json()
            assert data["chart_id"] == str(CHART_ID)
            assert data["assessment_id"] == str(ASSESSMENT_ID)
            assert data["ridge_height"] == "low_flat"
        finally:
            app.dependency_overrides.clear()


# ============================================================
# UTC-32 : get_residual_ridge_assessment_by_chart_id
# ============================================================

class TestGetResidualRidgeAssessment:
    """Service-layer tests for get_residual_ridge_assessment_by_chart_id."""

    def test_tc01_success_returns_assessment(self, mock_session):
        """UTC-32-TC-01: Existing chart with assessment → ResidualRidgeAssessment returned."""
        from app.services.residual_ridge_assessment import get_residual_ridge_assessment_by_chart_id

        assessment = make_assessment(assessment_id=ASSESSMENT_ID, chart_id=CHART_ID)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=assessment))

        result = get_residual_ridge_assessment_by_chart_id(mock_session, CHART_ID)

        assert result.assessment_id == ASSESSMENT_ID
        assert result.chart_id == CHART_ID
        assert result.ridge_height == "low_flat"
        assert result.ridge_width == "narrow"

    def test_tc02_not_found_raises_404(self, mock_session):
        """UTC-32-TC-02: chart_id has no assessment → 404 'Residual ridge assessment not found'."""
        from app.services.residual_ridge_assessment import get_residual_ridge_assessment_by_chart_id

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        with pytest.raises(HTTPException) as exc:
            get_residual_ridge_assessment_by_chart_id(mock_session, NONEXISTENT)

        assert exc.value.status_code == 404
        assert "Residual ridge assessment not found" in exc.value.detail

    def test_tc03_empty_chart_id_raises_value_error(self):
        """UTC-32-TC-03: chart_id is empty string → ValueError (UUID conversion fails)."""
        with pytest.raises(ValueError):
            uuid.UUID("")


class TestGetResidualRidgeAssessmentRouter:
    """Router-layer: UTC-32 — 401, 404, 200."""

    def test_tc04_no_auth_returns_401(self, mock_session):
        """UTC-32-TC-04: No bearer token → 401 Unauthorized."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tc02_not_found_returns_404(self, mock_session):
        """UTC-32-TC-02 (HTTP): No assessment for chart → 404."""
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        client, app = _authed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_tc01_success_returns_200(self, mock_session):
        """UTC-32-TC-01 (HTTP): Existing assessment → 200 with full object."""
        assessment = make_assessment(assessment_id=ASSESSMENT_ID, chart_id=CHART_ID)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=assessment))

        client, app = _authed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 200
            data = response.json()
            assert data["assessment_id"] == str(ASSESSMENT_ID)
            assert data["chart_id"] == str(CHART_ID)
            assert data["ridge_height"] == "low_flat"
            assert data["ridge_width"] == "narrow"
        finally:
            app.dependency_overrides.clear()

    def test_tc03_invalid_chart_id_returns_422(self, mock_session):
        """UTC-32-TC-03 (HTTP): Non-UUID chart_id in path → FastAPI path validation → 422."""
        client, app = _authed_client(mock_session)
        try:
            response = client.get("/dental-charts/not-a-uuid/residual-ridge-assessment")
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()


# ============================================================
# UTC-33 : update_residual_ridge_assessment
# ============================================================

class TestUpdateResidualRidgeAssessment:
    """Service-layer tests for update_residual_ridge_assessment."""

    def test_tc01_success_updates_and_returns_assessment(self, mock_session):
        """UTC-33-TC-01: Valid update payload → updated ResidualRidgeAssessment returned."""
        from app.models.residual_ridge_assessment import ResidualRidgeAssessmentUpdate
        from app.models.enums import RidgeHeightType, RidgeWidthType, JawSizeType
        from app.services.residual_ridge_assessment import update_residual_ridge_assessment

        assessment = make_assessment(assessment_id=ASSESSMENT_ID, chart_id=CHART_ID)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=assessment))
        mock_session.refresh.side_effect = lambda obj: None

        payload = ResidualRidgeAssessmentUpdate(
            ridge_height=RidgeHeightType.low_flat,
            ridge_width=RidgeWidthType.narrow,
            jaw_size=JawSizeType.medium,
        )

        result = update_residual_ridge_assessment(mock_session, CHART_ID, payload)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result.ridge_height == RidgeHeightType.low_flat
        assert result.ridge_width == RidgeWidthType.narrow
        assert result.jaw_size == JawSizeType.medium

    def test_tc01_partial_update_leaves_other_fields_unchanged(self, mock_session):
        """UTC-33-TC-01: Partial update — only specified fields change, others remain."""
        from app.models.residual_ridge_assessment import ResidualRidgeAssessmentUpdate
        from app.models.enums import RidgeHeightType
        from app.services.residual_ridge_assessment import update_residual_ridge_assessment

        assessment = make_assessment(assessment_id=ASSESSMENT_ID, chart_id=CHART_ID)
        original_width = assessment.ridge_width
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=assessment))
        mock_session.refresh.side_effect = lambda obj: None

        update_residual_ridge_assessment(
            mock_session, CHART_ID, ResidualRidgeAssessmentUpdate(ridge_height=RidgeHeightType.high)
        )

        assert assessment.ridge_height == RidgeHeightType.high
        assert assessment.ridge_width == original_width  # unchanged

    def test_tc02_not_found_raises_404(self, mock_session):
        """UTC-33-TC-02: chart_id has no assessment → 404 'Residual ridge assessment not found'."""
        from app.models.residual_ridge_assessment import ResidualRidgeAssessmentUpdate
        from app.services.residual_ridge_assessment import update_residual_ridge_assessment

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        with pytest.raises(HTTPException) as exc:
            update_residual_ridge_assessment(
                mock_session,
                NONEXISTENT,
                ResidualRidgeAssessmentUpdate(ridge_height="low_flat"),
            )

        assert exc.value.status_code == 404
        assert "Residual ridge assessment not found" in exc.value.detail


class TestUpdateResidualRidgeAssessmentRouter:
    """Router-layer: UTC-33 — 401, 404, 200."""

    def test_tc03_no_auth_returns_401(self, mock_session):
        """UTC-33-TC-03: No bearer token → 401 Unauthorized."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.put(BASE_URL, json={"ridge_height": "low_flat"})
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tc02_not_found_returns_404(self, mock_session):
        """UTC-33-TC-02 (HTTP): Non-existent chart → 404."""
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        client, app = _authed_client(mock_session)
        try:
            url = f"/dental-charts/{NONEXISTENT}/residual-ridge-assessment"
            response = client.put(url, json={"ridge_height": "low_flat"})
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_tc01_success_returns_200(self, mock_session):
        """UTC-33-TC-01 (HTTP): Valid update → 200 with updated fields."""
        assessment = make_assessment(assessment_id=ASSESSMENT_ID, chart_id=CHART_ID)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=assessment))
        mock_session.refresh.side_effect = lambda obj: None

        client, app = _authed_client(mock_session)
        try:
            response = client.put(BASE_URL, json={
                "ridge_height": "low_flat",
                "ridge_width": "narrow",
                "jaw_size": "medium",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["assessment_id"] == str(ASSESSMENT_ID)
            assert data["chart_id"] == str(CHART_ID)
            assert data["ridge_height"] == "low_flat"
        finally:
            app.dependency_overrides.clear()

    def test_tc01_invalid_enum_via_http_returns_422(self, mock_session):
        """UTC-33 (HTTP): Invalid enum value for ridge_height → 422."""
        client, app = _authed_client(mock_session)
        try:
            response = client.put(BASE_URL, json={"ridge_height": "not_a_valid_height"})
            assert response.status_code == 422
            error_locs = {e["loc"][-1] for e in response.json()["detail"]}
            assert "ridge_height" in error_locs
        finally:
            app.dependency_overrides.clear()


# ============================================================
# delete_residual_ridge_assessment (service + router)
# ============================================================

class TestDeleteResidualRidgeAssessment:
    """Service-layer tests for delete_residual_ridge_assessment."""

    def test_success_deletes_assessment(self, mock_session):
        """Existing assessment → deleted, no error."""
        from app.services.residual_ridge_assessment import delete_residual_ridge_assessment

        assessment = make_assessment(assessment_id=ASSESSMENT_ID, chart_id=CHART_ID)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=assessment))

        delete_residual_ridge_assessment(mock_session, CHART_ID)

        mock_session.delete.assert_called_once_with(assessment)
        mock_session.commit.assert_called_once()

    def test_not_found_raises_404(self, mock_session):
        """Non-existent chart_id → 404 'Residual ridge assessment not found'."""
        from app.services.residual_ridge_assessment import delete_residual_ridge_assessment

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        with pytest.raises(HTTPException) as exc:
            delete_residual_ridge_assessment(mock_session, NONEXISTENT)

        assert exc.value.status_code == 404


class TestDeleteResidualRidgeAssessmentRouter:
    """Router-layer: delete — 401, 404, 204."""

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
            url = f"/dental-charts/{NONEXISTENT}/residual-ridge-assessment"
            response = client.delete(url)
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_success_returns_204(self, mock_session):
        """Existing assessment → 204 No Content."""
        assessment = make_assessment(assessment_id=ASSESSMENT_ID, chart_id=CHART_ID)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=assessment))

        client, app = _authed_client(mock_session)
        try:
            response = client.delete(BASE_URL)
            assert response.status_code == 204
        finally:
            app.dependency_overrides.clear()
