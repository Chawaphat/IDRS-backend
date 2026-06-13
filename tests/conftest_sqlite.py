"""
SQLite in-memory fixtures for integration tests.

These fixtures create a real database engine, run DDL to build all tables,
and provide a Session that exercises actual SQL rather than MagicMock calls.
"""
import uuid
from typing import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine

# Import only the table models needed for patient integration tests.
# We deliberately avoid models that use PostgreSQL-only types (e.g. ARRAY)
# which SQLite cannot compile.
from app.models.profile import Profile  # noqa: F401
from app.models.patient import Patient  # noqa: F401
from app.models.dental_chart import DentalChart  # noqa: F401


_SQLITE_TABLES = [Profile.__table__, Patient.__table__, DentalChart.__table__]


@pytest.fixture(scope="session")
def sqlite_engine():
    """One SQLite in-memory engine shared across the whole test session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine, tables=_SQLITE_TABLES)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(sqlite_engine) -> Generator[Session, None, None]:
    """
    Per-test transactional session.

    Each test gets a fresh transaction that is rolled back on teardown so
    tests remain isolated without rebuilding the schema every time.
    """
    connection = sqlite_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# Shared UUIDs – match the values used in the mock-session tests so IDs are
# comparable across both test suites.
# ---------------------------------------------------------------------------

DENTIST_ID = uuid.UUID("036f8d6a-483d-4c03-9438-a501ec78291a")
ANOTHER_DENTIST_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


@pytest.fixture
def dentist_profile(db_session: Session):
    """Persist a real Profile row that patients can reference via FK."""
    from app.models.profile import Profile
    from app.models.enums import UserRole

    profile = Profile(
        id=DENTIST_ID,
        full_name="Dr. Test Dentist",
        role=UserRole.dentist,
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


@pytest.fixture
def another_dentist_profile(db_session: Session):
    """A second dentist used for cross-ownership / isolation tests."""
    from app.models.profile import Profile
    from app.models.enums import UserRole

    profile = Profile(
        id=ANOTHER_DENTIST_ID,
        full_name="Dr. Other Dentist",
        role=UserRole.dentist,
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile
