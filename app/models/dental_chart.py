from datetime import date, datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, Column, DateTime, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import AllergyStatusType, PatientExpectationsType

if TYPE_CHECKING:
    from app.models.dental_status import DentalStatus
    from app.models.esthetic_evaluation import EstheticEvaluation
    from app.models.extraoral_exam import ExtraoralExam
    from app.models.image_management import ImageManagement
    from app.models.occlusal_analysis import OcclusalAnalysis
    from app.models.patient import Patient
    from app.models.profile import Profile
    from app.models.vdo_evaluation import VdoEvaluation


class DentalChartBase(SQLModel):
    patient_id: uuid.UUID = Field(foreign_key="patients.patient_id")
    dentist_id: uuid.UUID | None = Field(default=None, foreign_key="profiles.id")
    record_date: date = Field(default_factory=date.today)
    chief_complaint: str | None = None
    present_illness: str | None = None
    medical_history: str | None = None
    regular_doctor_visits: bool = False
    current_medication: str | None = None
    allergy_status: AllergyStatusType = Field(
        sa_column=Column(SAEnum(AllergyStatusType, name="allergy_status_type"), nullable=False)
    )
    allergy_detail: str | None = None
    dental_history: str | None = None
    patient_expectation: list[PatientExpectationsType] | None = Field(
        default=None,
        sa_column=Column(ARRAY(SAEnum(PatientExpectationsType, name="patient_expectations_type"))),
    )
    patient_expectation_other: str | None = None
    patient_self_evaluation: str | None = None
    patient_expected_outcome: str | None = None


class DentalChart(DentalChartBase, table=True):
    __tablename__ = "dental_charts"

    chart_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )

    # patient คือ - relationship กับ model Patient ซึ่งจะทำให้สามารถเข้าถึงข้อมูล patient ที่เกี่ยวข้องกับ dental_chart นี้ได้ผ่าน dental_chart.patient
    # back_populates คือ - ใช้เพื่อบอกว่า relationship นี้เชื่อมกับ field dental_charts ใน model Patient ซึ่งจะทำให้สามารถเข้าถึง dental_charts ของ patient
    patient: "Patient" = Relationship(back_populates="dental_charts")
    dentist: "Profile" = Relationship(back_populates="dental_charts")
    extraoral_exams: list["ExtraoralExam"] = Relationship()
    esthetic_evaluations: list["EstheticEvaluation"] = Relationship()
    vdo_evaluations: list["VdoEvaluation"] = Relationship()
    dental_status_records: list["DentalStatus"] = Relationship(back_populates="chart")
    occlusal_analyses: list["OcclusalAnalysis"] = Relationship(back_populates="chart")
    images: list["ImageManagement"] = Relationship()


class DentalChartCreate(DentalChartBase):
    pass


class DentalChartUpdate(SQLModel):
    dentist_id: uuid.UUID | None = None
    record_date: date | None = None
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
