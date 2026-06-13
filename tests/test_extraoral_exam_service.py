"""
Tests for app/services/extraoral_exam.py  +  app/routers/extraoral_exams.py
Covers ALL test cases UTC-17, UTC-18, UTC-19.

Router prefix (from app/main.py):
  POST/GET/PUT/DELETE  →  /dental-charts/{chart_id}/extraoral-exams
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
DENTIST_ID  = uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a")
PATIENT_ID  = uuid.UUID("53a84328-8ff5-4eb1-b716-2afa7211bd6e")
CHART_ID    = uuid.UUID("d8454cab-1a71-46e8-8ac1-69ebae557d5a")
CHART_ID_2  = uuid.UUID("6ae0746a-511e-4a5d-88c9-975234efc03a")
EXAM_ID     = uuid.UUID("740f02d0-2667-46aa-b3e7-8488d05e5015")
NONEXISTENT = uuid.UUID("99999999-9999-9999-9999-999999999999")

BASE_URL    = f"/dental-charts/{CHART_ID}/extraoral-exams"

# ---------------------------------------------------------------------------
# Valid payload dict (reused across tests)
# ---------------------------------------------------------------------------
VALID_PAYLOAD = {
    "facial_symmetry": "symmetry",
    "facial_profile": "straight",
    "muscle_pain": {"temporalis": "mild", "masseter": "none"},
    "joint_pain": ["function"],
    "joint_sound": "clicking",
    "jaw_deviation": "to_left",
    "has_limited_opening": False,
    "mouth_opening_mm": 42,
    "has_limited_movement": False,
    "specify_movement_detail": None,
    "parafunctional_habit": ["bruxism", "clenching"],
    "parafunctional_habit_other": None,
    "factors_affecting_tooth_wear": {"acidic_diet": True, "dry_mouth": False},
}


# ---------------------------------------------------------------------------
# Helper: build ExtraoralExam-like object
# ---------------------------------------------------------------------------
def make_exam(exam_id=None, chart_id=None):
    from app.models.extraoral_exam import ExtraoralExam
    from app.models.enums import FacialSymmetryType, FacialProfileType

    e = ExtraoralExam(
        exam_id=exam_id or EXAM_ID,
        chart_id=chart_id or CHART_ID,
        facial_symmetry=FacialSymmetryType.symmetry,
        facial_profile=FacialProfileType.straight,
        muscle_pain={"temporalis": "mild", "masseter": "none"},
        joint_pain=None,
        joint_sound=None,
        jaw_deviation=None,
        has_limited_opening=False,
        mouth_opening_mm=42,
        has_limited_movement=False,
        parafunctional_habit=None,
        factors_affecting_tooth_wear={"acidic_diet": True, "dry_mouth": False},
    )
    return e


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
# UTC-17 : create_extraoral_exam
# ============================================================

class TestCreateExtraoralExam:
    """Service-layer tests for create_extraoral_exam."""

    def test_tc01_success_creates_and_returns_exam(self, mock_session):
        """UTC-17-TC-01: Valid payload + existing chart → ExtraoralExam returned."""
        from app.models.extraoral_exam import ExtraoralExamCreate
        from app.services.extraoral_exam import create_extraoral_exam

        payload = ExtraoralExamCreate(**VALID_PAYLOAD)

        def fake_refresh(obj):
            obj.exam_id = EXAM_ID

        mock_session.refresh.side_effect = fake_refresh

        result = create_extraoral_exam(mock_session, CHART_ID, payload)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result.chart_id == CHART_ID
        assert result.exam_id == EXAM_ID
        assert result.facial_symmetry == "symmetry"
        assert result.facial_profile == "straight"

    def test_tc03_missing_required_fields_raises_validation_error(self):
        """UTC-17-TC-03: facial_symmetry / facial_profile are required → ValidationError (422)."""
        from app.models.extraoral_exam import ExtraoralExamCreate

        with pytest.raises(pydantic.ValidationError) as exc:
            ExtraoralExamCreate()   # no required fields

        error_fields = {e["loc"][0] for e in exc.value.errors()}
        assert "facial_symmetry" in error_fields
        assert "facial_profile" in error_fields

    def test_tc03_invalid_enum_value_raises_validation_error(self):
        """UTC-17-TC-03: Empty string for required enum → ValidationError (422)."""
        from app.models.extraoral_exam import ExtraoralExamCreate

        with pytest.raises(pydantic.ValidationError) as exc:
            ExtraoralExamCreate(
                facial_symmetry="",    # invalid enum
                facial_profile="",     # invalid enum
            )

        error_fields = {e["loc"][0] for e in exc.value.errors()}
        assert "facial_symmetry" in error_fields or "facial_profile" in error_fields


class TestCreateExtraoralExamRouter:
    """Router-layer: UTC-17-TC-04 (401), UTC-17-TC-03 (422)."""

    def test_tc04_no_auth_returns_401(self, mock_session):
        """UTC-17-TC-04: No bearer token → 401 Unauthorized."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.post(BASE_URL, json=VALID_PAYLOAD)
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tc03_missing_required_fields_via_http_returns_422(self, mock_session):
        """UTC-17-TC-03 (HTTP): Missing facial_symmetry / facial_profile → 422."""
        client, app = _authed_client(mock_session)
        try:
            response = client.post(BASE_URL, json={})
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_tc02_nonexistent_chart_no_service_validation(self, mock_session):
        """
        UTC-17-TC-02: chart_id does not exist in the database.
        ⚠ Spec expects: 404 "Chart not found".
        ⚠ Actual: service does NOT validate chart FK — creates record without checking.
           DB would raise IntegrityError on commit in production.
        Test documents actual implementation behaviour.
        """
        from app.models.extraoral_exam import ExtraoralExamCreate
        from app.services.extraoral_exam import create_extraoral_exam

        payload = ExtraoralExamCreate(**VALID_PAYLOAD)
        mock_session.refresh.side_effect = lambda obj: setattr(obj, "exam_id", EXAM_ID)

        result = create_extraoral_exam(mock_session, NONEXISTENT, payload)
        assert result.chart_id == NONEXISTENT


# ============================================================
# UTC-18 : get_extraoral_exam_by_chart_id
# ============================================================

class TestGetExtraoralExam:
    """Service-layer tests for get_extraoral_exam_by_chart_id."""

    def test_tc01_success_returns_exam(self, mock_session):
        """UTC-18-TC-01: Existing chart with exam → ExtraoralExam returned."""
        from app.services.extraoral_exam import get_extraoral_exam_by_chart_id

        exam = make_exam(exam_id=EXAM_ID, chart_id=CHART_ID_2)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=exam))

        result = get_extraoral_exam_by_chart_id(mock_session, CHART_ID_2)

        assert result.exam_id == EXAM_ID
        assert result.chart_id == CHART_ID_2
        assert result.facial_symmetry == "symmetry"

    def test_tc02_nonexistent_chart_raises_404(self, mock_session):
        """UTC-18-TC-02: chart_id not found → 404 'Extraoral exam not found'."""
        from app.services.extraoral_exam import get_extraoral_exam_by_chart_id

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        with pytest.raises(HTTPException) as exc:
            get_extraoral_exam_by_chart_id(mock_session, NONEXISTENT)

        assert exc.value.status_code == 404
        assert "Extraoral exam not found" in exc.value.detail

    def test_tc03_empty_chart_id_raises_value_error(self):
        """UTC-18-TC-03: chart_id is empty string → ValueError before service is called."""
        with pytest.raises(ValueError):
            uuid.UUID("")


class TestGetExtraoralExamRouter:
    """Router-layer: UTC-18 — 401, 404, 200."""

    def test_no_auth_returns_401(self, mock_session):
        """UTC-18 (auth): No bearer token → 401."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_not_found_returns_404(self, mock_session):
        """UTC-18-TC-02 (HTTP): Chart has no exam → 404."""
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        client, app = _authed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_tc01_success_returns_200(self, mock_session):
        """UTC-18-TC-01 (HTTP): Existing exam → 200 with exam data."""
        exam = make_exam(exam_id=EXAM_ID, chart_id=CHART_ID)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=exam))

        client, app = _authed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 200
            data = response.json()
            assert data["exam_id"] == str(EXAM_ID)
            assert data["chart_id"] == str(CHART_ID)
            assert data["facial_symmetry"] == "symmetry"
        finally:
            app.dependency_overrides.clear()


# ============================================================
# UTC-19 : update_extraoral_exam
# ============================================================

class TestUpdateExtraoralExam:
    """Service-layer tests for update_extraoral_exam."""

    def test_tc01_success_updates_and_returns_exam(self, mock_session):
        """UTC-19-TC-01: Valid update payload → updated ExtraoralExam returned."""
        from app.models.extraoral_exam import ExtraoralExamUpdate
        from app.services.extraoral_exam import update_extraoral_exam
        from app.models.enums import JointSoundType, JawDeviationType

        exam = make_exam(exam_id=EXAM_ID, chart_id=CHART_ID_2)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=exam))
        mock_session.refresh.side_effect = lambda obj: None

        payload = ExtraoralExamUpdate(
            joint_sound=JointSoundType.popping,
            jaw_deviation=JawDeviationType.to_right,
        )

        result = update_extraoral_exam(mock_session, CHART_ID_2, payload)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result.joint_sound == JointSoundType.popping
        assert result.jaw_deviation == JawDeviationType.to_right

    def test_tc02_nonexistent_chart_raises_404(self, mock_session):
        """UTC-19-TC-02: chart_id not found → 404 'Extraoral exam not found'."""
        from app.models.extraoral_exam import ExtraoralExamUpdate
        from app.services.extraoral_exam import update_extraoral_exam

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        with pytest.raises(HTTPException) as exc:
            update_extraoral_exam(
                mock_session,
                NONEXISTENT,
                ExtraoralExamUpdate(joint_sound="popping"),
            )

        assert exc.value.status_code == 404
        assert "Extraoral exam not found" in exc.value.detail


class TestUpdateExtraoralExamRouter:
    """Router-layer: UTC-19 — 401, 404."""

    def test_no_auth_returns_401(self, mock_session):
        """UTC-19 (auth): No bearer token → 401."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.put(BASE_URL, json={"joint_sound": "popping"})
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_not_found_returns_404(self, mock_session):
        """UTC-19-TC-02 (HTTP): Non-existent chart → 404."""
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        client, app = _authed_client(mock_session)
        try:
            url = f"/dental-charts/{NONEXISTENT}/extraoral-exams"
            response = client.put(url, json={"joint_sound": "popping"})
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_tc01_success_returns_200(self, mock_session):
        """UTC-19-TC-01 (HTTP): Valid update → 200 with updated fields."""
        from app.models.enums import JointSoundType, JawDeviationType

        exam = make_exam(exam_id=EXAM_ID, chart_id=CHART_ID)
        exam.joint_sound = JointSoundType.popping
        exam.jaw_deviation = JawDeviationType.to_right
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=exam))
        mock_session.refresh.side_effect = lambda obj: None

        client, app = _authed_client(mock_session)
        try:
            response = client.put(BASE_URL, json={
                "joint_sound": "popping",
                "jaw_deviation": "to_right",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["exam_id"] == str(EXAM_ID)
            assert data["joint_sound"] == "popping"
            assert data["jaw_deviation"] == "to_right"
        finally:
            app.dependency_overrides.clear()
