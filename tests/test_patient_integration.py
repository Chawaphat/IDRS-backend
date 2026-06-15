"""
Integration tests for patient CRUD using a real SQLite in-memory database.

These tests exercise the actual SQL layer – no MagicMock sessions.
Each test commits real rows, queries them back, and verifies persistence.
"""
# Tell pytest to load fixtures from conftest_sqlite.py (not auto-loaded by default
# since only conftest.py files are collected automatically).
pytest_plugins = ["tests.conftest_sqlite"]

import uuid

import pytest
from fastapi import HTTPException

from tests.conftest_sqlite import DENTIST_ID, ANOTHER_DENTIST_ID


# ============================================================
# INT-01 : create_patient
# ============================================================

class TestCreatePatientIntegration:
    """Verify create_patient persists data and returns a live ORM object."""

    def test_persists_patient_with_correct_fields(self, db_session, dentist_profile):
        from app.models.patient import PatientCreate
        from app.services.patient import create_patient

        payload = PatientCreate(
            hn_number="HN-INT-001",
            name="Alice Integration",
            sex="female",
            age=28,
            phone="0812345678",
            allergy="penicillin",
        )

        patient = create_patient(db_session, payload, DENTIST_ID)

        assert patient.patient_id is not None, "patient_id must be assigned by DB"
        assert patient.hn_number == "HN-INT-001"
        assert patient.name == "Alice Integration"
        assert patient.sex == "female"
        assert patient.age == 28
        assert patient.phone == "0812345678"
        assert patient.allergy == "penicillin"
        assert patient.dentist_id == DENTIST_ID

    def test_created_at_is_populated(self, db_session, dentist_profile):
        from app.models.patient import PatientCreate
        from app.services.patient import create_patient

        payload = PatientCreate(hn_number="HN-INT-002", name="Bob")
        patient = create_patient(db_session, payload, DENTIST_ID)

        assert patient.created_at is not None

    def test_row_is_retrievable_after_commit(self, db_session, dentist_profile):
        """Data written to the DB must survive a fresh session.get() lookup."""
        from app.models.patient import Patient, PatientCreate
        from app.services.patient import create_patient

        payload = PatientCreate(hn_number="HN-INT-003", name="Carol")
        patient = create_patient(db_session, payload, DENTIST_ID)

        # Re-query from the same (still open) session to prove SQL was executed
        fetched = db_session.get(Patient, patient.patient_id)
        assert fetched is not None
        assert fetched.name == "Carol"

    def test_unique_hn_number_constraint(self, db_session, dentist_profile):
        """Inserting two patients with the same hn_number must raise an error."""
        from sqlalchemy.exc import IntegrityError
        from app.models.patient import PatientCreate
        from app.services.patient import create_patient

        create_patient(db_session, PatientCreate(hn_number="HN-DUP", name="First"), DENTIST_ID)

        with pytest.raises(IntegrityError):
            create_patient(db_session, PatientCreate(hn_number="HN-DUP", name="Second"), DENTIST_ID)


# ============================================================
# INT-02 : get_patient_by_id
# ============================================================

class TestGetPatientByIdIntegration:
    """Verify get_patient_by_id reads from the real DB and enforces ownership."""

    def _create(self, db_session, hn, name, dentist_id=DENTIST_ID):
        from app.models.patient import PatientCreate
        from app.services.patient import create_patient
        return create_patient(db_session, PatientCreate(hn_number=hn, name=name), dentist_id)

    def test_returns_correct_patient(self, db_session, dentist_profile):
        from app.services.patient import get_patient_by_id

        created = self._create(db_session, "HN-GET-001", "Dave")
        fetched = get_patient_by_id(db_session, created.patient_id, DENTIST_ID)

        assert fetched.patient_id == created.patient_id
        assert fetched.name == "Dave"

    def test_nonexistent_id_raises_404(self, db_session, dentist_profile):
        from app.services.patient import get_patient_by_id

        with pytest.raises(HTTPException) as exc:
            get_patient_by_id(db_session, uuid.uuid4(), DENTIST_ID)
        assert exc.value.status_code == 404

    def test_cross_dentist_ownership_raises_404(
        self, db_session, dentist_profile, another_dentist_profile
    ):
        """A patient owned by dentist A must not be visible to dentist B."""
        from app.services.patient import get_patient_by_id

        patient = self._create(db_session, "HN-GET-002", "Eve", dentist_id=DENTIST_ID)

        with pytest.raises(HTTPException) as exc:
            get_patient_by_id(db_session, patient.patient_id, ANOTHER_DENTIST_ID)
        assert exc.value.status_code == 404


# ============================================================
# INT-03 : update_patient
# ============================================================

class TestUpdatePatientIntegration:
    """Verify update_patient writes changed fields back to the DB."""

    def _create(self, db_session, hn="HN-UPD-001", name="Frank"):
        from app.models.patient import PatientCreate
        from app.services.patient import create_patient
        return create_patient(db_session, PatientCreate(hn_number=hn, name=name), DENTIST_ID)

    def test_name_update_persists(self, db_session, dentist_profile):
        from app.models.patient import Patient, PatientUpdate
        from app.services.patient import update_patient

        patient = self._create(db_session)
        pid = patient.patient_id

        updated = update_patient(db_session, pid, PatientUpdate(name="Frank Updated"), DENTIST_ID)
        assert updated.name == "Frank Updated"

        # Re-fetch from DB to confirm persistence
        refetched = db_session.get(Patient, pid)
        assert refetched.name == "Frank Updated"

    def test_partial_update_leaves_other_fields_unchanged(self, db_session, dentist_profile):
        from app.models.patient import PatientUpdate
        from app.services.patient import update_patient

        patient = self._create(db_session, hn="HN-UPD-002", name="Grace")
        original_hn = patient.hn_number

        update_patient(db_session, patient.patient_id, PatientUpdate(age=40), DENTIST_ID)

        from app.models.patient import Patient
        refetched = db_session.get(Patient, patient.patient_id)
        assert refetched.age == 40
        assert refetched.hn_number == original_hn  # unchanged

    def test_update_nonexistent_raises_404(self, db_session, dentist_profile):
        from app.models.patient import PatientUpdate
        from app.services.patient import update_patient

        with pytest.raises(HTTPException) as exc:
            update_patient(db_session, uuid.uuid4(), PatientUpdate(name="Ghost"), DENTIST_ID)
        assert exc.value.status_code == 404


# ============================================================
# INT-04 : delete_patient
# ============================================================

class TestDeletePatientIntegration:
    """Verify delete_patient removes the row from the DB."""

    def test_deleted_row_is_gone(self, db_session, dentist_profile):
        from app.models.patient import Patient, PatientCreate
        from app.services.patient import create_patient, delete_patient

        patient = create_patient(
            db_session, PatientCreate(hn_number="HN-DEL-001", name="Henry"), DENTIST_ID
        )
        pid = patient.patient_id

        delete_patient(db_session, pid, DENTIST_ID)

        assert db_session.get(Patient, pid) is None, "Row must not exist after deletion"

    def test_delete_nonexistent_raises_404(self, db_session, dentist_profile):
        from app.services.patient import delete_patient

        with pytest.raises(HTTPException) as exc:
            delete_patient(db_session, uuid.uuid4(), DENTIST_ID)
        assert exc.value.status_code == 404

    def test_cross_dentist_delete_raises_404(
        self, db_session, dentist_profile, another_dentist_profile
    ):
        """Dentist B must not be able to delete a patient owned by dentist A."""
        from app.models.patient import Patient, PatientCreate
        from app.services.patient import create_patient, delete_patient

        patient = create_patient(
            db_session, PatientCreate(hn_number="HN-DEL-002", name="Iris"), DENTIST_ID
        )

        with pytest.raises(HTTPException) as exc:
            delete_patient(db_session, patient.patient_id, ANOTHER_DENTIST_ID)
        assert exc.value.status_code == 404

        # Row must still exist
        assert db_session.get(Patient, patient.patient_id) is not None
