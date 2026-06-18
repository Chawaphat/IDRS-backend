"""
Tests for app/services/vdo_evaluation.py  +  app/routers/vdo_evaluations.py
Covers ALL test cases UTC-25, UTC-26, UTC-27.

Router prefix (from app/main.py):
  POST/GET/PUT/DELETE  →  /dental-charts/{chart_id}/vdo-evaluation

Behavioural notes:
  - All VdoEvaluationBase fields are optional — empty payload is valid at schema level.
  - UTC-25-TC-03: spec triggers 422 via invalid bite_type enum value ("") → tested.
  - get_vdo_evaluation_by_chart_id raises 404 correctly (matches spec for UTC-26-TC-02).
  - update_vdo_evaluation raises 404 when record absent (matches spec for UTC-27-TC-02).
"""
import uuid
from unittest.mock import MagicMock

import pydantic
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from tests.conftest import make_profile

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DENTIST_ID  = uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a")
CHART_ID    = uuid.UUID("6ae0746a-511e-4a5d-88c9-975234efc03a")
VDO_ID      = uuid.UUID("2d2ddb74-4d56-4fb0-a6b8-024eaf20fa7d")
NONEXISTENT = uuid.UUID("99999999-9999-9999-9999-999999999999")

BASE_URL    = f"/dental-charts/{CHART_ID}/vdo-evaluation"

# ---------------------------------------------------------------------------
# Valid payload dict (matches UTC-25-TC-01)
# ---------------------------------------------------------------------------
VALID_PAYLOAD = {
    "facial_soft_tissue": ["nasolabial_fold", "thin_lips"],
    "closest_speaking": 2.0,
    "free_way_space": 3.0,
    "bite_type": "normal_bite",
    "reference_teeth": [11, 21, 31, 41],
}


# ---------------------------------------------------------------------------
# Helper: build VdoEvaluation-like object
# ---------------------------------------------------------------------------
def make_vdo(vdo_id=None, chart_id=None):
    from app.models.vdo_evaluation import VdoEvaluation
    from app.models.enums import BiteType, FacialConditionType

    v = VdoEvaluation(
        vdo_id=vdo_id or VDO_ID,
        chart_id=chart_id or CHART_ID,
        facial_soft_tissue=[FacialConditionType.nasolabial_fold, FacialConditionType.thin_lips],
        closest_speaking=2.0,
        free_way_space=3.0,
        bite_type=BiteType.normal_bite,
        reference_teeth=[11, 21, 31, 41],
    )
    return v


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
# UTC-25 : create_vdo_evaluation
# ============================================================

class TestCreateVdoEvaluation:
    """Service-layer tests for create_vdo_evaluation."""

    def test_tc01_success_creates_and_returns_evaluation(self, mock_session):
        """UTC-25-TC-01: Valid payload → VdoEvaluation created and returned."""
        from app.models.vdo_evaluation import VdoEvaluationCreate
        from app.services.vdo_evaluation import create_vdo_evaluation

        payload = VdoEvaluationCreate(**VALID_PAYLOAD)

        def fake_refresh(obj):
            obj.vdo_id = VDO_ID

        mock_session.refresh.side_effect = fake_refresh

        result = create_vdo_evaluation(mock_session, CHART_ID, payload)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result.chart_id == CHART_ID
        assert result.vdo_id == VDO_ID
        assert result.bite_type == "normal_bite"
        assert result.closest_speaking == 2.0
        assert result.free_way_space == 3.0
        assert result.reference_teeth == [11, 21, 31, 41]

    def test_tc02_nonexistent_chart_raises_404(self, mock_session):
        """UTC-25-TC-02: chart_id does not exist → 404 'Chart not found'."""
        from app.models.vdo_evaluation import VdoEvaluationCreate
        from app.services.vdo_evaluation import create_vdo_evaluation

        payload = VdoEvaluationCreate(**VALID_PAYLOAD)
        mock_session.get.return_value = None

        with pytest.raises(HTTPException) as exc:
            create_vdo_evaluation(mock_session, NONEXISTENT, payload)

        assert exc.value.status_code == 404
        assert "Chart not found" in exc.value.detail

    def test_tc03_invalid_bite_type_raises_validation_error(self):
        """UTC-25-TC-03: Invalid enum value for bite_type → Pydantic ValidationError (422)."""
        from app.models.vdo_evaluation import VdoEvaluationCreate

        with pytest.raises(pydantic.ValidationError) as exc:
            VdoEvaluationCreate(bite_type="")   # empty string not in BiteType enum

        error_fields = {e["loc"][0] for e in exc.value.errors()}
        assert "bite_type" in error_fields

    def test_tc03_invalid_facial_soft_tissue_raises_validation_error(self):
        """UTC-25-TC-03: Invalid enum value in facial_soft_tissue list → ValidationError."""
        from app.models.vdo_evaluation import VdoEvaluationCreate

        with pytest.raises(pydantic.ValidationError):
            VdoEvaluationCreate(facial_soft_tissue=["not_a_valid_condition"])


class TestCreateVdoEvaluationRouter:
    """Router-layer: UTC-25-TC-04 (401), UTC-25-TC-03 (422)."""

    def test_tc04_no_auth_returns_401(self, mock_session):
        """UTC-25-TC-04: No bearer token → 401 Unauthorized."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.post(BASE_URL, json=VALID_PAYLOAD)
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tc03_invalid_bite_type_via_http_returns_422(self, mock_session):
        """UTC-25-TC-03 (HTTP): Invalid bite_type enum → 422."""
        client, app = _authed_client(mock_session)
        try:
            bad_payload = {**VALID_PAYLOAD, "bite_type": "not_a_bite_type"}
            response = client.post(BASE_URL, json=bad_payload)
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_tc01_success_returns_201(self, mock_session):
        """UTC-25-TC-01 (HTTP): Valid payload → 201 Created with vdo_id."""
        mock_session.refresh.side_effect = lambda obj: setattr(obj, "vdo_id", VDO_ID)

        client, app = _authed_client(mock_session)
        try:
            response = client.post(BASE_URL, json=VALID_PAYLOAD)
            assert response.status_code == 201
            data = response.json()
            assert data["chart_id"] == str(CHART_ID)
            assert data["vdo_id"] == str(VDO_ID)
            assert data["bite_type"] == "normal_bite"
            assert data["closest_speaking"] == 2.0
        finally:
            app.dependency_overrides.clear()


# ============================================================
# UTC-26 : get_vdo_evaluation_by_chart_id
# ============================================================

class TestGetVdoEvaluation:
    """Service-layer tests for get_vdo_evaluation_by_chart_id."""

    def test_tc01_success_returns_evaluation(self, mock_session):
        """UTC-26-TC-01: Existing chart with VDO evaluation → returned."""
        from app.services.vdo_evaluation import get_vdo_evaluation_by_chart_id

        vdo = make_vdo(vdo_id=VDO_ID, chart_id=CHART_ID)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=vdo))

        result = get_vdo_evaluation_by_chart_id(mock_session, CHART_ID)

        assert result.vdo_id == VDO_ID
        assert result.chart_id == CHART_ID
        assert result.bite_type == "normal_bite"
        assert result.closest_speaking == 2.0
        assert result.free_way_space == 3.0
        assert result.reference_teeth == [11, 21, 31, 41]

    def test_tc02_not_found_raises_404(self, mock_session):
        """UTC-26-TC-02: chart_id has no VDO evaluation → 404 'VDO evaluation not found'."""
        from app.services.vdo_evaluation import get_vdo_evaluation_by_chart_id

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        with pytest.raises(HTTPException) as exc:
            get_vdo_evaluation_by_chart_id(mock_session, NONEXISTENT)

        assert exc.value.status_code == 404
        assert "VDO evaluation not found" in exc.value.detail

    def test_tc03_empty_chart_id_raises_value_error(self):
        """UTC-26-TC-03: Empty chart_id string → ValueError (UUID conversion fails)."""
        with pytest.raises(ValueError):
            uuid.UUID("")


class TestGetVdoEvaluationRouter:
    """Router-layer: UTC-26 — 401, 404, 200."""

    def test_tc04_no_auth_returns_401(self, mock_session):
        """UTC-26-TC-04: No bearer token → 401."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tc02_not_found_returns_404(self, mock_session):
        """UTC-26-TC-02 (HTTP): No VDO evaluation for chart → 404."""
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        client, app = _authed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_tc01_success_returns_200(self, mock_session):
        """UTC-26-TC-01 (HTTP): Existing VDO evaluation → 200 with full object."""
        vdo = make_vdo(vdo_id=VDO_ID, chart_id=CHART_ID)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=vdo))

        client, app = _authed_client(mock_session)
        try:
            response = client.get(BASE_URL)
            assert response.status_code == 200
            data = response.json()
            assert data["vdo_id"] == str(VDO_ID)
            assert data["chart_id"] == str(CHART_ID)
            assert data["bite_type"] == "normal_bite"
            assert data["closest_speaking"] == 2.0
            assert data["free_way_space"] == 3.0
            assert data["reference_teeth"] == [11, 21, 31, 41]
        finally:
            app.dependency_overrides.clear()


# ============================================================
# UTC-27 : update_vdo_evaluation
# ============================================================

class TestUpdateVdoEvaluation:
    """Service-layer tests for update_vdo_evaluation."""

    def test_tc01_success_updates_and_returns_evaluation(self, mock_session):
        """UTC-27-TC-01: Valid update payload → updated VdoEvaluation returned."""
        from app.models.vdo_evaluation import VdoEvaluationUpdate
        from app.models.enums import BiteType, FacialConditionType
        from app.services.vdo_evaluation import update_vdo_evaluation

        vdo = make_vdo(vdo_id=VDO_ID, chart_id=CHART_ID)
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=vdo))
        mock_session.refresh.side_effect = lambda obj: None

        payload = VdoEvaluationUpdate(
            facial_soft_tissue=[FacialConditionType.drooping_commissure],
            free_way_space=2.5,
            bite_type=BiteType.deep_bite,
            reference_teeth=[13, 23],
        )

        result = update_vdo_evaluation(mock_session, CHART_ID, payload)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result.facial_soft_tissue == [FacialConditionType.drooping_commissure]
        assert result.free_way_space == 2.5
        assert result.bite_type == BiteType.deep_bite
        assert result.reference_teeth == [13, 23]

    def test_tc02_not_found_raises_404(self, mock_session):
        """UTC-27-TC-02: chart_id has no VDO evaluation → 404."""
        from app.models.vdo_evaluation import VdoEvaluationUpdate
        from app.services.vdo_evaluation import update_vdo_evaluation

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        with pytest.raises(HTTPException) as exc:
            update_vdo_evaluation(
                mock_session,
                NONEXISTENT,
                VdoEvaluationUpdate(free_way_space=2.5),
            )

        assert exc.value.status_code == 404
        assert "VDO evaluation not found" in exc.value.detail


class TestUpdateVdoEvaluationRouter:
    """Router-layer: UTC-27 — 401, 404, 200."""

    def test_tc03_no_auth_returns_401(self, mock_session):
        """UTC-27-TC-03: No bearer token → 401."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.put(BASE_URL, json={"free_way_space": 2.5})
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tc02_not_found_returns_404(self, mock_session):
        """UTC-27-TC-02 (HTTP): Non-existent chart → 404."""
        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=None))

        client, app = _authed_client(mock_session)
        try:
            url = f"/dental-charts/{NONEXISTENT}/vdo-evaluation"
            response = client.put(url, json={"free_way_space": 2.5})
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_tc01_success_returns_200(self, mock_session):
        """UTC-27-TC-01 (HTTP): Valid update → 200 with updated fields."""
        from app.models.enums import BiteType, FacialConditionType

        vdo = make_vdo(vdo_id=VDO_ID, chart_id=CHART_ID)
        vdo.facial_soft_tissue = [FacialConditionType.drooping_commissure]
        vdo.free_way_space = 2.5
        vdo.bite_type = BiteType.deep_bite
        vdo.reference_teeth = [13, 23]

        mock_session.exec.return_value = MagicMock(first=MagicMock(return_value=vdo))
        mock_session.refresh.side_effect = lambda obj: None

        client, app = _authed_client(mock_session)
        try:
            response = client.put(BASE_URL, json={
                "facial_soft_tissue": ["drooping_commissure"],
                "free_way_space": 2.5,
                "bite_type": "deep_bite",
                "reference_teeth": [13, 23],
            })
            assert response.status_code == 200
            data = response.json()
            assert data["vdo_id"] == str(VDO_ID)
            assert data["chart_id"] == str(CHART_ID)
            assert data["free_way_space"] == 2.5
            assert data["bite_type"] == "deep_bite"
            assert data["reference_teeth"] == [13, 23]
        finally:
            app.dependency_overrides.clear()
