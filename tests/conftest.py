"""Shared pytest fixtures for all service tests."""
import sys
import uuid
from datetime import date, datetime
from types import ModuleType
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Stub out optional heavy dependencies before any app module is imported.
# This lets tests run without a live Supabase connection.
# ---------------------------------------------------------------------------
def _make_stub(name: str) -> ModuleType:
    mod = ModuleType(name)
    sys.modules[name] = mod
    return mod

if "supabase" not in sys.modules:
    _supabase = _make_stub("supabase")
    _supabase.create_client = MagicMock()
    _supabase.Client = MagicMock()

if "supabase_auth" not in sys.modules:
    _sb_auth = _make_stub("supabase_auth")
    _sb_auth.Session = MagicMock()  # used as a type-hint in authen.py

# The AI inference stack (torch / numpy / requests / pillow) is only needed to
# actually run the Dentex model. Service-layer unit tests mock
# `ai_inference.predict`, so stub the heavy imports to keep the suite runnable
# on a machine without the ML dependencies installed.
for _heavy in ("numpy", "requests", "torch"):
    if _heavy not in sys.modules:
        _make_stub(_heavy)

if "PIL" not in sys.modules:
    _pil = _make_stub("PIL")
    _pil_image = _make_stub("PIL.Image")
    _pil.Image = _pil_image

if "app.ai_models.seunet_arch" not in sys.modules:
    _seunet = _make_stub("app.ai_models.seunet_arch")
    _seunet.SEUNet = MagicMock()


@pytest.fixture(autouse=True)
def _patch_db_init(monkeypatch):
    """
    Prevent create_db_and_tables() from trying to connect to a real DB
    during FastAPI startup for every test that uses a TestClient.
    """
    # Patch where it is *used* (app.main imports it directly)
    monkeypatch.setattr("app.main.create_db_and_tables", lambda: None, raising=False)


@pytest.fixture
def mock_session():
    """Return a MagicMock that stands in for a SQLModel Session."""
    return MagicMock()


@pytest.fixture
def dentist_id():
    return uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a")


@pytest.fixture
def patient_id():
    return uuid.UUID("3fb0f7b1-da69-4793-a7c7-a6f441dd2f23")


@pytest.fixture
def chart_id():
    return uuid.UUID("d8454cab-1a71-46e8-8ac1-69ebae557d5a")


@pytest.fixture
def another_chart_id():
    return uuid.UUID("6ae0746a-511e-4a5d-88c9-975234efc03a")


def make_patient(patient_id=None, dentist_id=None, **kwargs):
    """Helper to build a minimal Patient-like object without hitting the DB."""
    from app.models.patient import Patient

    p = Patient(
        patient_id=patient_id or uuid.uuid4(),
        hn_number=kwargs.get("hn_number", "HN001"),
        name=kwargs.get("name", "John Doe"),
        sex=kwargs.get("sex", "male"),
        age=kwargs.get("age", 32),
        phone=kwargs.get("phone", "09032332"),
        dentist_id=dentist_id or uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a"),
        created_at=datetime.utcnow(),
    )
    return p


def make_chart(chart_id=None, patient_id=None, dentist_id=None):
    from app.models.dental_chart import DentalChart

    c = DentalChart(
        chart_id=chart_id or uuid.uuid4(),
        patient_id=patient_id or uuid.uuid4(),
        dentist_id=dentist_id or uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a"),
        record_date=date.today(),
        created_at=datetime.utcnow(),
    )
    return c


def make_profile(dentist_id=None):
    """Build a MagicMock that satisfies get_current_profile / require_chart_editor."""
    profile = MagicMock()
    profile.id = dentist_id or uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a")
    profile.role = "dentist"
    return profile


@pytest.fixture
def test_app(mock_session):
    """
    Return a FastAPI TestClient with:
    - get_session overridden → mock_session
    - get_current_profile overridden → a fake dentist profile
    Individual tests can further override get_current_profile to raise 401.
    """
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.database import get_session
    from app.core.authen import get_current_profile

    fake_profile = make_profile()

    app.dependency_overrides[get_session] = lambda: mock_session
    app.dependency_overrides[get_current_profile] = lambda: fake_profile

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client

    app.dependency_overrides.clear()
