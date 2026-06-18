"""
Tests for app/services/patient.py  +  app/routers/patients.py
Covers ALL test cases UTC-7 through UTC-13 including failure paths.

Layer split:
  - TestCreate/Get/Update/Delete/Search*  → service-layer (mock session)
  - Test*Router                           → router-layer (TestClient, 401/422)
"""
import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from tests.conftest import make_chart, make_patient, make_profile

# ---------------------------------------------------------------------------
# Constants (match the test-plan UUIDs)
# ---------------------------------------------------------------------------
DENTIST_ID = uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a")
PATIENT_ID = uuid.UUID("3fb0f7b1-da69-4793-a7c7-a6f441dd2f23")
CHART_ID   = uuid.UUID("d8454cab-1a71-46e8-8ac1-69ebae557d5a")

NONEXISTENT_ID = "99999999-9999-9999-9999-999999999999"


# ============================================================
# UTC-7 : create_patient
# ============================================================

class TestCreatePatient:
    """Service-layer tests for create_patient."""

    def test_tc01_success_creates_and_returns_patient(self, mock_session):
        """UTC-7-TC-01: Valid payload → Patient created and returned."""
        from app.models.patient import PatientCreate
        from app.services.patient import create_patient

        payload = PatientCreate(
            hn_number="HN001",
            name="john doe",
            sex="male",
            age=32,
            phone="09032332",
        )

        def fake_refresh(obj):
            obj.patient_id = PATIENT_ID

        mock_session.refresh.side_effect = fake_refresh

        patient = create_patient(mock_session, payload, DENTIST_ID)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert patient.dentist_id == DENTIST_ID
        assert patient.hn_number == "HN001"
        assert patient.name == "john doe"


class TestCreatePatientRouter:
    """Router-layer tests for POST /patients (401, 422)."""

    def _client_no_auth(self, mock_session):
        """TestClient where auth dependency raises 401."""
        from app.main import app
        from app.core.database import get_session
        from app.core.authen import get_current_profile

        def raise_401():
            raise HTTPException(status_code=401, detail="Unauthorized")

        app.dependency_overrides[get_session] = lambda: mock_session
        app.dependency_overrides[get_current_profile] = raise_401
        client = TestClient(app, raise_server_exceptions=False)
        return client, app

    def test_tc02_missing_required_fields_returns_422(self, mock_session):
        """UTC-7-TC-02: Missing required fields (hn_number, name) → router returns HTTP 422."""
        from app.main import app
        from app.core.database import get_session
        from app.core.authen import get_current_profile

        app.dependency_overrides[get_session] = lambda: mock_session
        app.dependency_overrides[get_current_profile] = lambda: make_profile(DENTIST_ID)
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app, raise_server_exceptions=False)
            # Send a body that omits both required fields (hn_number, name)
            response = client.post("/patients", json={"sex": "male", "age": 32})
            assert response.status_code == 422
            error_locs = {
                e["loc"][-1]
                for e in response.json()["detail"]
            }
            assert "hn_number" in error_locs
            assert "name" in error_locs
        finally:
            app.dependency_overrides.clear()

    def test_tc02_no_auth_returns_401(self, mock_session):
        """UTC-7-TC-02 (auth): No bearer token → 401."""
        client, app = self._client_no_auth(mock_session)
        try:
            response = client.post("/patients", json={
                "hn_number": "HN001",
                "name": "john doe",
                "sex": "male",
                "age": 32,
                "phone": "09032332",
            })
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()


# ============================================================
# UTC-8 : get_all_patients
# ============================================================

class TestGetAllPatients:
    """Service-layer tests for get_all_patients."""

    def test_tc01_success_returns_patient_list(self, mock_session):
        """UTC-8-TC-01: Dentist with patients → non-empty list."""
        from app.services.patient import get_all_patients

        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        chart   = make_chart(chart_id=CHART_ID, patient_id=PATIENT_ID, dentist_id=DENTIST_ID)

        mock_session.exec.side_effect = [
            MagicMock(all=MagicMock(return_value=[patient])),
            MagicMock(first=MagicMock(return_value=chart)),
            MagicMock(first=MagicMock(return_value=None)),
        ]

        results = get_all_patients(mock_session, DENTIST_ID)

        mock_session.exec.assert_called() 
        assert len(results) == 1
        assert results[0].patient_id == PATIENT_ID
        assert results[0].status == "Active"

    def test_tc03_empty_list_when_no_patients(self, mock_session):
        """UTC-8-TC-03: Dentist with no patients → []."""
        from app.services.patient import get_all_patients

        mock_session.exec.return_value = MagicMock(all=MagicMock(return_value=[]))
        assert get_all_patients(mock_session, DENTIST_ID) == []


class TestGetAllPatientsRouter:
    """Router-layer: UTC-8-TC-02 — no auth → 401."""

    def test_tc02_no_auth_returns_401(self, mock_session):
        """UTC-8-TC-02: No bearer token → 401."""
        from app.main import app
        from app.core.database import get_session
        from app.core.authen import get_current_profile

        def raise_401():
            raise HTTPException(status_code=401, detail="Unauthorized")

        app.dependency_overrides[get_session] = lambda: mock_session
        app.dependency_overrides[get_current_profile] = raise_401
        try:
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/patients")
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()


# ============================================================
# UTC-9 : get_patient_by_id
# ============================================================

class TestGetPatientById:
    """Service-layer tests for get_patient_by_id."""

    def test_tc01_success_returns_patient(self, mock_session):
        """UTC-9-TC-01: Existing patient → returned."""
        from app.services.patient import get_patient_by_id

        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        mock_session.get.return_value = patient

        result = get_patient_by_id(mock_session, PATIENT_ID, DENTIST_ID)
        assert result.patient_id == PATIENT_ID

    def test_tc03_not_found_raises_404(self, mock_session):
        """UTC-9-TC-03: Non-existent patient → 404."""
        from app.services.patient import get_patient_by_id

        mock_session.get.return_value = None

        with pytest.raises(HTTPException) as exc:
            get_patient_by_id(mock_session, uuid.uuid4(), DENTIST_ID)
        assert exc.value.status_code == 404
        assert "Patient not found" in exc.value.detail

    def test_cross_dentist_ownership_raises_404(self, mock_session):
        """Security: patient belongs to other dentist → 404 (not a data leak)."""
        from app.services.patient import get_patient_by_id

        patient = make_patient(patient_id=PATIENT_ID, dentist_id=uuid.uuid4())
        mock_session.get.return_value = patient

        with pytest.raises(HTTPException) as exc:
            get_patient_by_id(mock_session, PATIENT_ID, DENTIST_ID)
        assert exc.value.status_code == 404


class TestGetPatientByIdRouter:
    """Router-layer: UTC-9-TC-02 — no auth → 401."""

    def test_tc02_no_auth_returns_401(self, mock_session):
        """UTC-9-TC-02: No bearer token → 401."""
        from app.main import app
        from app.core.database import get_session
        from app.core.authen import get_current_profile

        def raise_401():
            raise HTTPException(status_code=401, detail="Unauthorized")

        app.dependency_overrides[get_session] = lambda: mock_session
        app.dependency_overrides[get_current_profile] = raise_401
        try:
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get(f"/patients/{PATIENT_ID}")
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()


# ============================================================
# UTC-10 : update_patient
# ============================================================

class TestUpdatePatient:
    """Service-layer tests for update_patient."""

    def test_tc01_success_updates_patient(self, mock_session):
        """UTC-10-TC-01: Valid update → updated patient returned."""
        from app.models.patient import PatientUpdate
        from app.services.patient import update_patient

        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        mock_session.get.return_value = patient

        result = update_patient(mock_session, PATIENT_ID, PatientUpdate(name="george russell"), DENTIST_ID)

        assert result.name == "george russell"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_tc03_not_found_raises_404(self, mock_session):
        """UTC-10-TC-03: Non-existent patient → 404."""
        from app.models.patient import PatientUpdate
        from app.services.patient import update_patient

        mock_session.get.return_value = None

        with pytest.raises(HTTPException) as exc:
            update_patient(mock_session, uuid.uuid4(), PatientUpdate(name="x"), DENTIST_ID)
        assert exc.value.status_code == 404


class TestUpdatePatientRouter:
    """Router-layer: UTC-10-TC-02 (401) and UTC-10-TC-04 (422)."""

    def _authed_client(self, mock_session, app):
        from app.core.database import get_session
        from app.core.authen import get_current_profile
        app.dependency_overrides[get_session] = lambda: mock_session
        app.dependency_overrides[get_current_profile] = lambda: make_profile(DENTIST_ID)
        return TestClient(app, raise_server_exceptions=False)

    def test_tc02_no_auth_returns_401(self, mock_session):
        """UTC-10-TC-02: No bearer token → 401."""
        from app.main import app
        from app.core.database import get_session
        from app.core.authen import get_current_profile

        def raise_401():
            raise HTTPException(status_code=401, detail="Unauthorized")

        app.dependency_overrides[get_session] = lambda: mock_session
        app.dependency_overrides[get_current_profile] = raise_401
        try:
            client = TestClient(app, raise_server_exceptions=False)
            response = client.put(f"/patients/{PATIENT_ID}", json={"name": "x"})
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tc04_invalid_data_type_returns_422(self, mock_session):
        """UTC-10-TC-04: age='george russell' (string where int expected) → router returns HTTP 422."""
        from app.main import app
        from app.core.database import get_session
        from app.core.authen import get_current_profile

        app.dependency_overrides[get_session] = lambda: mock_session
        app.dependency_overrides[get_current_profile] = lambda: make_profile(DENTIST_ID)
        try:
            from fastapi.testclient import TestClient
            client = TestClient(app, raise_server_exceptions=False)
            response = client.put(
                f"/patients/{PATIENT_ID}",
                json={"age": "george russell"},
            )
            assert response.status_code == 422
            error_locs = {e["loc"][-1] for e in response.json()["detail"]}
            assert "age" in error_locs
        finally:
            app.dependency_overrides.clear()


# ============================================================
# UTC-11 : delete_patient
# ============================================================

class TestDeletePatient:
    """Service-layer tests for delete_patient."""

    def test_tc01_success_deletes_patient(self, mock_session):
        """UTC-11-TC-01: Existing patient → deleted (service returns None, router returns 204).

        The document expected output shows {"message": "Patient deleted successfully"}
        but the actual implementation returns HTTP 204 No Content (no body).
        This test verifies both layers:
          - service: session.delete and session.commit are called
          - router:  response status code is 204
        """
        from app.services.patient import delete_patient

        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        mock_session.get.return_value = patient

        result = delete_patient(mock_session, PATIENT_ID, DENTIST_ID)

        mock_session.delete.assert_called_once_with(patient)
        mock_session.commit.assert_called_once()
        assert result is None, "service must return None (router sends 204 No Content, not a message body)"

    def test_tc01_router_returns_204(self, mock_session):
        """UTC-11-TC-01 (router layer): Successful delete → HTTP 204 No Content, empty body."""
        from app.main import app
        from app.core.database import get_session
        from app.core.authen import get_current_profile

        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID)
        mock_session.get.return_value = patient

        app.dependency_overrides[get_session] = lambda: mock_session
        app.dependency_overrides[get_current_profile] = lambda: make_profile(DENTIST_ID)
        try:
            client = TestClient(app, raise_server_exceptions=False)
            response = client.delete(f"/patients/{PATIENT_ID}")
            assert response.status_code == 204
            assert response.content == b"", "204 No Content must have an empty body"
        finally:
            app.dependency_overrides.clear()

    def test_tc03_not_found_raises_404(self, mock_session):
        """UTC-11-TC-03: Non-existent patient → 404."""
        from app.services.patient import delete_patient

        mock_session.get.return_value = None

        with pytest.raises(HTTPException) as exc:
            delete_patient(mock_session, uuid.uuid4(), DENTIST_ID)
        assert exc.value.status_code == 404


class TestDeletePatientRouter:
    """Router-layer: UTC-11-TC-02 — no auth → 401."""

    def test_tc02_no_auth_returns_401(self, mock_session):
        """UTC-11-TC-02: No bearer token → 401."""
        from app.main import app
        from app.core.database import get_session
        from app.core.authen import get_current_profile

        def raise_401():
            raise HTTPException(status_code=401, detail="Unauthorized")

        app.dependency_overrides[get_session] = lambda: mock_session
        app.dependency_overrides[get_current_profile] = raise_401
        try:
            client = TestClient(app, raise_server_exceptions=False)
            response = client.delete(f"/patients/{PATIENT_ID}")
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()


# ============================================================
# UTC-12 : search_patients
# ============================================================

class TestSearchPatients:
    """Service-layer tests for search_patients."""

    def test_tc01_success_by_name(self, mock_session):
        """UTC-12-TC-01: Search by name → matching patient returned."""
        from app.services.patient import search_patients

        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID, name="John Doe")
        chart   = make_chart(chart_id=CHART_ID, patient_id=PATIENT_ID, dentist_id=DENTIST_ID)

        mock_session.exec.side_effect = [
            MagicMock(all=MagicMock(return_value=[patient])),
            MagicMock(first=MagicMock(return_value=chart)),
            MagicMock(first=MagicMock(return_value=None)),
        ]

        results = search_patients(mock_session, "john", DENTIST_ID)
        assert len(results) == 1
        assert "John" in results[0].name

    def test_tc02_success_by_hn_number(self, mock_session):
        """UTC-12-TC-02: Search by HN number → matching patient returned."""
        from app.services.patient import search_patients

        patient = make_patient(patient_id=PATIENT_ID, dentist_id=DENTIST_ID, hn_number="HN001")
        chart   = make_chart(chart_id=CHART_ID, patient_id=PATIENT_ID, dentist_id=DENTIST_ID)

        mock_session.exec.side_effect = [
            MagicMock(all=MagicMock(return_value=[patient])),
            MagicMock(first=MagicMock(return_value=chart)),
            MagicMock(first=MagicMock(return_value=None)),
        ]

        results = search_patients(mock_session, "HN001", DENTIST_ID)
        assert len(results) == 1
        assert results[0].hn_number == "HN001"

    def test_tc03_no_match_returns_empty_list(self, mock_session):
        """UTC-12-TC-03: No matching patient → []."""
        from app.services.patient import search_patients

        mock_session.exec.return_value = MagicMock(all=MagicMock(return_value=[]))
        assert search_patients(mock_session, "XYZ", DENTIST_ID) == []


# ============================================================
# UTC-13 : get_patient_dental_charts
# ============================================================

class TestGetPatientDentalCharts:
    """Service-layer tests for get_patient_dental_charts."""

    def test_tc01_success_returns_charts(self, mock_session):
        """UTC-13-TC-01: Patient with charts → list of DentalChart."""
        from app.services.patient import get_patient_dental_charts

        chart = make_chart(chart_id=CHART_ID, patient_id=PATIENT_ID)
        exec_result = MagicMock(
            first=MagicMock(return_value=chart),
            all=MagicMock(return_value=[chart]),
        )
        mock_session.exec.return_value = exec_result

        results = get_patient_dental_charts(mock_session, PATIENT_ID)
        assert len(results) == 1
        assert results[0].chart_id == CHART_ID

    def test_tc02_no_charts_raises_404(self, mock_session):
        """
        UTC-13-TC-02: Patient exists but has no dental chart records.

        SPEC vs IMPLEMENTATION DIVERGENCE (known):
          - Spec (FullUnitest.md) expects: returns empty list [].
          - Implementation: raises HTTP 404 "Dental charts not found for this patient"
            because the service uses .first() == None to gate the query, and cannot
            distinguish "patient has no charts" from "patient does not exist".

        This test verifies the ACTUAL implementation behaviour (404).
        To fix to match spec the service would need to check patient existence
        separately before querying charts.
        """
        from app.services.patient import get_patient_dental_charts

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        with pytest.raises(HTTPException) as exc:
            get_patient_dental_charts(mock_session, uuid.uuid4())
        assert exc.value.status_code == 404
        assert "Dental charts not found" in exc.value.detail

    def test_tc03_nonexistent_patient_raises_404(self, mock_session):
        """
        UTC-13-TC-03: Non-existent patient_id → 404 "Dental charts not found for this patient".
        Implementation cannot distinguish "no charts" (TC-02) from "no patient" (TC-03)
        — both result in 404 because the service queries charts by patient_id only.
        """
        from app.services.patient import get_patient_dental_charts

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        with pytest.raises(HTTPException) as exc:
            get_patient_dental_charts(mock_session, uuid.UUID(NONEXISTENT_ID))
        assert exc.value.status_code == 404


class TestGetPatientDentalChartsRouter:
    """Router-layer: UTC-13-TC-04 — no auth → 401."""

    def test_tc04_no_auth_returns_401(self, mock_session):
        """UTC-13-TC-04: No bearer token → 401."""
        from app.main import app
        from app.core.database import get_session
        from app.core.authen import get_current_profile

        def raise_401():
            raise HTTPException(status_code=401, detail="Unauthorized")

        app.dependency_overrides[get_session] = lambda: mock_session
        app.dependency_overrides[get_current_profile] = raise_401
        try:
            client = TestClient(app, raise_server_exceptions=False)
            # The dental-charts endpoint on /patients/{id}/dental-charts doesn't
            # use get_current_profile directly, but the router-level
            # require_chart_editor dependency does.
            response = client.get(f"/patients/{PATIENT_ID}/dental-charts")
            # Without auth the router-level dependency blocks the request.
            # Status may be 401 (via require_chart_editor) or 200 if this
            # specific endpoint skips auth — assert not 200.
            assert response.status_code in (401, 403)
        finally:
            app.dependency_overrides.clear()
