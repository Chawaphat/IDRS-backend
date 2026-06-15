"""
Tests for app/services/occlusal_contact.py  +  app/routers/occlusal_contact.py

Router prefix (from app/main.py):
  PUT    →  /dental-charts/{chart_id}/occlusal-contacts
  DELETE →  /dental-charts/{chart_id}/occlusal-contacts/{contact_id}
  Auth: require_chart_editor

Service behaviours:
  - create_and_replace_occlusal_contacts:
      • If no OcclusalAnalysis exists for chart_id → auto-creates one.
      • Deletes ALL existing contacts for that occlusal record, then inserts new ones.
  - delete_occlusal_contact: deletes single contact by contact_id (no 404 guard in service).
"""
import uuid
from unittest.mock import MagicMock, call

import pydantic
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from tests.conftest import make_profile

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DENTIST_ID   = uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a")
CHART_ID     = uuid.UUID("6ae0746a-511e-4a5d-88c9-975234efc03a")
OCCLUSAL_ID  = uuid.UUID("a1b2c3d4-1111-2222-3333-444444444444")
CONTACT_ID   = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
NONEXISTENT  = uuid.UUID("99999999-9999-9999-9999-999999999999")

BASE_URL        = f"/dental-charts/{CHART_ID}/occlusal-contacts"
CONTACT_URL     = f"{BASE_URL}/{CONTACT_ID}"

# ---------------------------------------------------------------------------
# Valid bulk payload dict
# ---------------------------------------------------------------------------
VALID_CONTACTS_PAYLOAD = {
    "contacts": [
        {"contact_type": "working", "upper_tooth": 16, "lower_tooth": 46},
        {"contact_type": "non_working", "upper_tooth": 26, "lower_tooth": 36},
    ]
}


# ---------------------------------------------------------------------------
# Helper: build OcclusalAnalysis object
# ---------------------------------------------------------------------------
def make_occlusal(occlusal_id=None, chart_id=None):
    from app.models.occlusal_analysis import OcclusalAnalysis

    o = OcclusalAnalysis(
        occlusal_id=occlusal_id or OCCLUSAL_ID,
        chart_id=chart_id or CHART_ID,
    )
    return o


# ---------------------------------------------------------------------------
# Helper: build OcclusalContact object
# ---------------------------------------------------------------------------
def make_contact(contact_id=None, occlusal_id=None, contact_type="working"):
    from app.models.occlusal_contact import OcclusalContact
    from app.models.enums import ContactType

    c = OcclusalContact(
        contact_id=contact_id or CONTACT_ID,
        occlusal_id=occlusal_id or OCCLUSAL_ID,
        contact_type=ContactType(contact_type),
        upper_tooth=16,
        lower_tooth=46,
    )
    return c


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
# create_and_replace_occlusal_contacts
# ============================================================

class TestCreateAndReplaceOcclusalContacts:
    """Service-layer tests for create_and_replace_occlusal_contacts."""

    def test_tc01_replaces_contacts_when_occlusal_exists(self, mock_session):
        """TC-01: Existing OcclusalAnalysis → old contacts deleted, new ones inserted."""
        from app.models.occlusal_contact import OcclusalContactBulkCreate, OcclusalContactCreate
        from app.models.enums import ContactType
        from app.services.occlusal_contact import create_and_replace_occlusal_contacts

        existing_occlusal = make_occlusal()
        old_contact = make_contact()

        # exec called twice: 1st for get_or_create_occlusal_analysis, 2nd for old contacts
        mock_session.exec.side_effect = [
            MagicMock(first=MagicMock(return_value=existing_occlusal)),
            MagicMock(all=MagicMock(return_value=[old_contact])),
        ]

        payload = OcclusalContactBulkCreate(contacts=[
            OcclusalContactCreate(contact_type=ContactType.working, upper_tooth=16, lower_tooth=46),
            OcclusalContactCreate(contact_type=ContactType.non_working, upper_tooth=26, lower_tooth=36),
        ])

        result = create_and_replace_occlusal_contacts(mock_session, CHART_ID, payload)

        mock_session.delete.assert_called_once_with(old_contact)
        mock_session.add_all.assert_called_once()
        mock_session.commit.assert_called_once()
        assert len(result) == 2

    def test_tc01_auto_creates_occlusal_when_missing(self, mock_session):
        """TC-01 (no occlusal): Missing OcclusalAnalysis → auto-created, then contacts inserted."""
        from app.models.occlusal_contact import OcclusalContactBulkCreate, OcclusalContactCreate
        from app.models.enums import ContactType
        from app.services.occlusal_contact import create_and_replace_occlusal_contacts

        new_occlusal = make_occlusal()

        def refresh_side_effect(obj):
            obj.occlusal_id = OCCLUSAL_ID

        # exec called twice: 1st returns None (no occlusal), 2nd returns [] (no old contacts)
        mock_session.exec.side_effect = [
            MagicMock(first=MagicMock(return_value=None)),
            MagicMock(all=MagicMock(return_value=[])),
        ]
        mock_session.refresh.side_effect = refresh_side_effect

        payload = OcclusalContactBulkCreate(contacts=[
            OcclusalContactCreate(contact_type=ContactType.working, upper_tooth=16, lower_tooth=46),
        ])

        result = create_and_replace_occlusal_contacts(mock_session, CHART_ID, payload)

        # add called for new OcclusalAnalysis, add_all for contacts
        assert mock_session.add.call_count == 1
        assert mock_session.add_all.call_count == 1
        assert len(result) == 1

    def test_tc03_invalid_contact_type_raises_validation_error(self):
        """TC-03 (schema): Invalid ContactType enum → Pydantic ValidationError."""
        from app.models.occlusal_contact import OcclusalContactCreate

        with pytest.raises(pydantic.ValidationError) as exc:
            OcclusalContactCreate(contact_type="INVALID_CONTACT", upper_tooth=16, lower_tooth=46)

        error_fields = {e["loc"][0] for e in exc.value.errors()}
        assert "contact_type" in error_fields

    def test_tc03_missing_required_fields_raises_validation_error(self):
        """TC-03 (schema): Missing upper_tooth / lower_tooth → Pydantic ValidationError."""
        from app.models.occlusal_contact import OcclusalContactCreate
        from app.models.enums import ContactType

        with pytest.raises(pydantic.ValidationError) as exc:
            OcclusalContactCreate(contact_type=ContactType.working)

        error_fields = {e["loc"][0] for e in exc.value.errors()}
        assert "upper_tooth" in error_fields
        assert "lower_tooth" in error_fields


class TestCreateAndReplaceOcclusalContactsRouter:
    """Router-layer: PUT /dental-charts/{chart_id}/occlusal-contacts."""

    def test_no_auth_returns_401(self, mock_session):
        """No bearer token → 401."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.put(BASE_URL, json=VALID_CONTACTS_PAYLOAD)
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tc03_invalid_contact_type_via_http_returns_422(self, mock_session):
        """TC-03 (HTTP): Invalid contact_type → 422."""
        client, app = _authed_client(mock_session)
        try:
            bad_payload = {"contacts": [{"contact_type": "INVALID_TYPE", "upper_tooth": 16, "lower_tooth": 46}]}
            response = client.put(BASE_URL, json=bad_payload)
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_tc03_missing_teeth_via_http_returns_422(self, mock_session):
        """TC-03 (HTTP): Missing upper_tooth / lower_tooth → 422."""
        client, app = _authed_client(mock_session)
        try:
            bad_payload = {"contacts": [{"contact_type": "working_contact"}]}
            response = client.put(BASE_URL, json=bad_payload)
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_tc01_success_returns_200(self, mock_session):
        """TC-01 (HTTP): Valid bulk contacts → 200 with list of contacts."""
        from app.models.enums import ContactType

        contact1 = make_contact(contact_id=uuid.uuid4(), contact_type="working")
        contact1.upper_tooth = 16
        contact1.lower_tooth = 46
        contact2 = make_contact(contact_id=uuid.uuid4(), contact_type="non_working")
        contact2.upper_tooth = 26
        contact2.lower_tooth = 36

        existing_occlusal = make_occlusal()
        mock_session.exec.side_effect = [
            MagicMock(first=MagicMock(return_value=existing_occlusal)),
            MagicMock(all=MagicMock(return_value=[])),
        ]

        # add_all assigns the new contact objects
        def fake_add_all(items):
            for item in items:
                item.contact_id = uuid.uuid4()

        mock_session.add_all.side_effect = fake_add_all

        client, app = _authed_client(mock_session)
        try:
            response = client.put(BASE_URL, json=VALID_CONTACTS_PAYLOAD)
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2
        finally:
            app.dependency_overrides.clear()


# ============================================================
# delete_occlusal_contact
# ============================================================

class TestDeleteOcclusalContact:
    """Service-layer tests for delete_occlusal_contact."""

    def test_success_deletes_contact(self, mock_session):
        """Existing contact → deleted."""
        from app.services.occlusal_contact import delete_occlusal_contact

        contact = make_contact()
        mock_session.get.return_value = contact

        delete_occlusal_contact(mock_session, CONTACT_ID)

        mock_session.delete.assert_called_once_with(contact)
        mock_session.commit.assert_called_once()

    def test_nonexistent_contact_service_does_not_validate(self, mock_session):
        """
        Non-existent contact_id.
        ⚠ Actual: service calls session.delete(None) — no 404 guard in service code.
           This would raise an error at SQLAlchemy level in production.
        Test documents actual implementation behaviour.
        """
        from app.services.occlusal_contact import delete_occlusal_contact

        mock_session.get.return_value = None

        # Service does not raise HTTPException — it passes None to session.delete
        delete_occlusal_contact(mock_session, NONEXISTENT)
        mock_session.delete.assert_called_once_with(None)


class TestDeleteOcclusalContactRouter:
    """Router-layer: DELETE /dental-charts/{chart_id}/occlusal-contacts/{contact_id}."""

    def test_no_auth_returns_401(self, mock_session):
        """No bearer token → 401."""
        client, app = _unauthed_client(mock_session)
        try:
            response = client.delete(CONTACT_URL)
            assert response.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_success_returns_204(self, mock_session):
        """Existing contact → 204 No Content."""
        contact = make_contact()
        mock_session.get.return_value = contact

        client, app = _authed_client(mock_session)
        try:
            response = client.delete(CONTACT_URL)
            assert response.status_code == 204
        finally:
            app.dependency_overrides.clear()
