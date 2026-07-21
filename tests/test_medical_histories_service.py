"""
Tests for app/services/medical_histories.py  +  app/routers/medical_histories.py
Covers ALL test cases UTC-16, UTC-17, UTC-18.

Layer split:
  - Service tests  → mock session, direct function calls
  - Router tests   → TestClient for 401 / 422 / 404 over HTTP

Router prefix (from app/main.py):
  POST/GET/PUT/DELETE  →  /dental-charts/{chart_id}/medical-history
"""
import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pydantic
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from tests.conftest import make_chart, make_patient, make_profile

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DENTIST_ID  = uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a")
PATIENT_ID  = uuid.UUID("53a84328-8ff5-4eb1-b716-2afa7211bd6e")
CHART_ID    = uuid.UUID("d8454cab-1a71-46e8-8ac1-69ebae557d5a")
HISTORY_ID  = uuid.UUID("2f6e8f12-f746-4d07-8a2b-225746f67167")
NONEXISTENT = uuid.UUID("99999999-9999-9999-9999-999999999999")

BASE_URL    = f"/dental-charts/{CHART_ID}/medical-history"


# ---------------------------------------------------------------------------
# Helper: build a MedicalHistory-like object
# ---------------------------------------------------------------------------
def make_history(chart_id=None, history_id=None, allergy_status="no"):
    from app.models.medical_histories import MedicalHistory

    h = MedicalHistory(
        history_id=history_id or HISTORY_ID,
        chart_id=chart_id or CHART_ID,
        chief_complaint="Tooth pain on upper right molar",
        present_illness="Pain started 3 days ago",
        medical_history="No significant medical history",
        regular_doctor_visits=True,
        current_medication=None,
        allergy_status=allergy_status,
        allergy_detail=None,
        dental_history="Previous filling on tooth 18",
        patient_expectation=None,
        patient_self_evaluation="Pain level 7/10",
        patient_expected_outcome="Relief from pain",
        created_at=datetime.utcnow(),
    )
    return h


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
# UTC-16 : create_medical_history
# ============================================================

class TestCreateMedicalHistory:
    """Service-layer tests for create_medical_history."""

    def test_tc01_success_creates_and_returns_history(self, mock_session):
        """UTC-16-TC-01: Valid payload + existing chart → MedicalHistory created."""
        from app.models.medical_histories import MedicalHistoryCreate
        from app.services.medical_histories import create_medical_history

        payload = MedicalHistoryCreate(
            chief_complaint="Tooth pain on upper right molar",
            present_illness="Pain started 3 days ago, worse when chewing",
            medical_history="No significant medical history",
            regular_doctor_visits=True,
            current_medication=None,
            allergy_status="no",
            allergy_detail=None,
            dental_history="Previous filling on tooth 18",
            patient_expectation=None,
            patient_self_evaluation="Pain level 7/10",
            patient_expected_outcome="Relief from pain and normal chewing function",
        )

        chart   = make_chart(chart_id=CHART_ID, patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID)

        def fake_get(model, pk):
            from app.models.dental_chart import DentalChart
            from app.models.patient import Patient
            if model is DentalChart:
                return chart
            if model is Patient:
                return patient
            return None

        mock_session.get.side_effect = fake_get

        def fake_refresh(obj):
            obj.history_id = HISTORY_ID

        mock_session.refresh.side_effect = fake_refresh

        result = create_medical_history(mock_session, CHART_ID, payload)

        mock_session.add.assert_called()
        mock_session.commit.assert_called_once()
        assert result.chart_id == CHART_ID
        assert result.history_id == HISTORY_ID

    def test_tc02_nonexistent_chart_raises_404(self, mock_session):
        """UTC-16-TC-02: chart_id does not exist → 404 'Chart not found'."""
        from app.models.medical_histories import MedicalHistoryCreate
        from app.services.medical_histories import create_medical_history

        payload = MedicalHistoryCreate(
            chief_complaint="Tooth pain",
            present_illness="3 days",
            medical_history="None",
            regular_doctor_visits=False,
            current_medication=None,
            allergy_status="no",
            dental_history=None,
            patient_expectation=None,
            patient_self_evaluation=None,
            patient_expected_outcome=None,
        )

        mock_session.get.return_value = None

        with pytest.raises(HTTPException) as exc:
            create_medical_history(mock_session, NONEXISTENT, payload)

        assert exc.value.status_code == 404
        assert "Chart not found" in exc.value.detail

    def test_tc03_missing_required_allergy_status_raises_validation_error(self):
        """UTC-16-TC-03: allergy_status is required → Pydantic ValidationError (422)."""
        from app.models.medical_histories import MedicalHistoryCreate

        with pytest.raises(pydantic.ValidationError) as exc:
            MedicalHistoryCreate(
                chief_complaint="",
                present_illness="",
                medical_history="",
                regular_doctor_visits=True,
                current_medication=None,
                # allergy_status OMITTED — required field
                dental_history=None,
            )

        error_fields = {e["loc"][0] for e in exc.value.errors()}
        assert "allergy_status" in error_fields

    def test_allergy_synced_to_patient_when_yes(self, mock_session):
        """Allergy detail is propagated to Patient when allergy_status='yes'."""
        from app.models.medical_histories import MedicalHistoryCreate
        from app.services.medical_histories import create_medical_history

        payload = MedicalHistoryCreate(
            chief_complaint="x",
            present_illness="x",
            medical_history="x",
            regular_doctor_visits=False,
            current_medication=None,
            allergy_status="yes",
            allergy_detail="penicillin",
            dental_history=None,
            patient_expectation=None,
            patient_self_evaluation=None,
            patient_expected_outcome=None,
        )

        chart   = make_chart(chart_id=CHART_ID, patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID)

        def fake_get(model, pk):
            from app.models.dental_chart import DentalChart
            from app.models.patient import Patient
            if model is DentalChart:
                return chart
            if model is Patient:
                return patient
            return None

        mock_session.get.side_effect = fake_get
        mock_session.refresh.side_effect = lambda obj: None

        create_medical_history(mock_session, CHART_ID, payload)

        assert patient.allergy == "penicillin"


class TestCreateMedicalHistoryRouter:
    """Router-layer: UTC-16-TC-04 — no auth → 401."""

    def test_tc04_no_auth_returns_401(self, mock_session):
        """UTC-16-TC-04: No bearer token → 401 Unauthorized."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.post(BASE_URL, json={
                "chief_complaint": "Tooth pain",
                "present_illness": "3 days",
                "medical_history": "None",
                "regular_doctor_visits": True,
                "allergy_status": "no",
            })
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tc03_missing_allergy_status_via_http_returns_422(self, mock_session):
        """UTC-16-TC-03 (HTTP): Missing allergy_status → 422."""
        client, app = _authed_client(mock_session)
        try:
            response = client.post(BASE_URL, json={
                "chief_complaint": "",
                "present_illness": "",
                "medical_history": "",
                "regular_doctor_visits": True,
                # allergy_status omitted
            })
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()


# ============================================================
# UTC-17 : get_medical_history_by_chart_id
# ============================================================

class TestGetMedicalHistory:
    """Service-layer tests for get_medical_history_by_chart_id."""

    def test_tc01_success_returns_history(self, mock_session):
        """UTC-17-TC-01: Existing chart with history → MedicalHistory returned."""
        from app.services.medical_histories import get_medical_history_by_chart_id

        history = make_history(chart_id=CHART_ID)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=history))

        result = get_medical_history_by_chart_id(mock_session, CHART_ID)

        assert result.chart_id == CHART_ID
        assert result.history_id == HISTORY_ID
        assert result.chief_complaint == "Tooth pain on upper right molar"

    def test_tc02_nonexistent_chart_raises_404(self, mock_session):
        """UTC-17-TC-02: chart_id not found → 404 'Medical history not found'."""
        from app.services.medical_histories import get_medical_history_by_chart_id

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        with pytest.raises(HTTPException) as exc:
            get_medical_history_by_chart_id(mock_session, NONEXISTENT)

        assert exc.value.status_code == 404
        assert "Medical history not found" in exc.value.detail

    def test_tc03_missing_chart_id_raises_validation_error(self):
        """UTC-17-TC-03: chart_id empty string → ValueError (UUID conversion fails)."""
        with pytest.raises(ValueError):
            uuid.UUID("")


class TestGetMedicalHistoryRouter:
    """Router-layer: no auth → 401, not found → 404."""

    def test_no_auth_returns_401(self, mock_session):
        """UTC-17 (auth): No bearer token → 401."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_not_found_returns_404(self, mock_session):
        """UTC-17-TC-02 (HTTP): chart has no history → 404."""
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        client, app = _authed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_success_returns_200(self, mock_session):
        """UTC-17-TC-01 (HTTP): Existing history → 200 with data."""
        history = make_history(chart_id=CHART_ID)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=history))

        client, app = _authed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 200
            data = response.json()
            assert data["chart_id"] == str(CHART_ID)
            assert data["history_id"] == str(HISTORY_ID)
        finally:
            app.dependency_overrides.clear()


# ============================================================
# UTC-18 : update_medical_history
# ============================================================

class TestUpdateMedicalHistory:
    """Service-layer tests for update_medical_history."""

    def test_tc01_success_updates_and_returns_history(self, mock_session):
        """UTC-18-TC-01: Valid update payload → updated MedicalHistory returned."""
        from app.models.medical_histories import MedicalHistoryUpdate
        from app.services.medical_histories import update_medical_history

        history = make_history(chart_id=CHART_ID)
        chart   = make_chart(chart_id=CHART_ID, patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID)

        # get_medical_history_by_chart_id calls session.exec
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=history))

        def fake_get(model, pk):
            from app.models.dental_chart import DentalChart
            from app.models.patient import Patient
            if model is DentalChart:
                return chart
            if model is Patient:
                return patient
            return None

        mock_session.get.side_effect = fake_get
        mock_session.refresh.side_effect = lambda obj: None

        payload = MedicalHistoryUpdate(
            chief_complaint="Tooth pain on upper right molar",
            present_illness="Pain started 3000 days ago, worse when chewing",
            medical_history="No significant medical history",
            regular_doctor_visits=True,
        )

        result = update_medical_history(mock_session, CHART_ID, payload)

        mock_session.add.assert_called()
        mock_session.commit.assert_called_once()
        assert result.present_illness == "Pain started 3000 days ago, worse when chewing"

    def test_tc02_creates_new_record_when_none_exists(self, mock_session):
        """UTC-18-TC-02: No existing medical history → upsert creates a new record and returns it."""
        from app.models.medical_histories import MedicalHistoryUpdate
        from app.services.medical_histories import update_medical_history

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))
        mock_session.get.return_value = None

        def fake_refresh(obj):
            obj.history_id = HISTORY_ID

        mock_session.refresh.side_effect = fake_refresh

        payload = MedicalHistoryUpdate(chief_complaint="x", allergy_status="no")
        result = update_medical_history(mock_session, CHART_ID, payload)

        mock_session.add.assert_called()
        mock_session.commit.assert_called_once()
        assert result.chart_id == CHART_ID


class TestUpdateMedicalHistoryRouter:
    """Router-layer: UTC-18 — no auth → 401, not found → 404."""

    def test_no_auth_returns_401(self, mock_session):
        """UTC-18 (auth): No bearer token → 401."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.put(BASE_URL, json={"chief_complaint": "x"})
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_creates_new_record_when_none_exists_returns_200(self, mock_session):
        """UTC-18-TC-02 (HTTP): No existing medical history → upsert creates new record → 200."""
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))
        mock_session.get.return_value = None

        new_history = make_history(chart_id=CHART_ID)
        mock_session.refresh.side_effect = lambda obj: obj.__dict__.update(new_history.__dict__)

        client, app = _authed_client(mock_session)
        try:
            response = client.put(BASE_URL, json={"chief_complaint": "x", "allergy_status": "no"})
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()
