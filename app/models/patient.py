from datetime import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.dental_chart import DentalChart


class PatientBase(SQLModel):
    hn_number: str = Field(max_length=20, sa_column_kwargs={"unique": True})    
    name: str = Field(max_length=255)
    sex: str | None = Field(default=None, max_length=10)
    age: int | None = None
    phone: str | None = Field(default=None, max_length=15)
    allergy: str | None = Field(default=None, max_length=20)

class Patient(PatientBase, table=True):
    __tablename__ = "patients"

    patient_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )

    dental_charts: list["DentalChart"] = Relationship(back_populates="patient")

class PatientCreate(PatientBase):
    pass

class PatientUpdate(SQLModel):
    hn_number: str | None = None
    name: str | None = None
    sex: str | None = None
    age: int | None = None
    phone: str | None = None
    allergy: str | None = None

class PatientWithClinicalSummary(PatientBase):
    patient_id: uuid.UUID
    created_at: datetime
    last_visit: datetime | None = None
    chief_complaint: str | None = None
    status: str = "Active"
