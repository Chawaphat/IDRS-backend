import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, Column, Enum as SAEnum
from sqlmodel import DateTime, Field, Relationship, SQLModel

from app.models.enums import (
    AllergyStatusType,
    PatientExpectationsType,
)

if TYPE_CHECKING:
    from app.models.dental_chart import DentalChart
    
class MedicalHistoryBase(SQLModel):
    chief_complaint: str | None = None
    present_illness: str | None = None
    medical_history: str | None = None
    regular_doctor_visits: bool = False
    current_medication: str | None = None
    allergy_status: AllergyStatusType          
    allergy_detail: str | None = None
    dental_history: str | None = None
    patient_expectation: list[PatientExpectationsType] | None = None
    patient_expectation_other: str | None = None
    patient_self_evaluation: str | None = None
    patient_expected_outcome: str | None = None


class MedicalHistory(MedicalHistoryBase, table=True):
    __tablename__ = "medical_histories"
    history_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chart_id: uuid.UUID = Field(foreign_key="dental_charts.chart_id", unique=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )
    
    allergy_status: AllergyStatusType = Field(
        sa_column=Column(SAEnum(AllergyStatusType, name="allergy_status_type"), nullable=False)
    )
    patient_expectation: list[PatientExpectationsType] | None = Field(
        default=None,
        sa_column=Column(ARRAY(SAEnum(PatientExpectationsType, name="patient_expectations_type"))),
    )
    chart: "DentalChart" = Relationship(back_populates="medical_history")
    
class MedicalHistoryCreate(MedicalHistoryBase):
    pass    

class MedicalHistoryUpdate(SQLModel):
    chief_complaint: str | None = None
    present_illness: str | None = None
    medical_history: str | None = None
    regular_doctor_visits: bool | None = None
    current_medication: str | None = None
    allergy_status: AllergyStatusType | None = None  
    allergy_detail: str | None = None
    dental_history: str | None = None
    patient_expectation: list[PatientExpectationsType] | None = None 
    patient_expectation_other: str | None = None
    patient_self_evaluation: str | None = None
    patient_expected_outcome: str | None = None