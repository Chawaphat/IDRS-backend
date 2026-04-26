from datetime import date, datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.models.medical_histories import MedicalHistory

if TYPE_CHECKING:
    from app.models.dental_status import DentalStatus
    from app.models.esthetic_evaluation import EstheticEvaluation
    from app.models.extraoral_exam import ExtraoralExam
    from app.models.image_management import ImageManagement
    from app.models.occlusal_analysis import OcclusalAnalysis
    from app.models.patient import Patient
    from app.models.profile import Profile
    from app.models.vdo_evaluation import VdoEvaluation
    from app.models.medical_histories import MedicalHistory


class DentalChartBase(SQLModel):
    patient_id: uuid.UUID = Field(foreign_key="patients.patient_id")
    dentist_id: uuid.UUID = Field(foreign_key="profiles.id")
    record_date: date = Field(default_factory=date.today)
    

class DentalChart(DentalChartBase, table=True):
    __tablename__ = "dental_charts"

    chart_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )

    # back_populates คือ - ใช้เพื่อบอกว่า relationship นี้เชื่อมกับ field dental_charts ใน model Patient ซึ่งจะทำให้สามารถเข้าถึง dental_charts ของ patient
    patient: "Patient" = Relationship(back_populates="dental_charts")
    dentist: "Profile" = Relationship(back_populates="dental_charts")
    medical_history: "MedicalHistory" = Relationship(back_populates="chart",sa_relationship_kwargs={"passive_deletes": True})
    extraoral_exams: "ExtraoralExam" = Relationship(back_populates="chart", sa_relationship_kwargs={"passive_deletes": True})
    esthetic_evaluations: "EstheticEvaluation" = Relationship(back_populates="chart", sa_relationship_kwargs={"passive_deletes": True})
    vdo_evaluations: "VdoEvaluation" = Relationship(back_populates="chart", sa_relationship_kwargs={"passive_deletes": True})
    dental_status_records: "DentalStatus" = Relationship(back_populates="chart", sa_relationship_kwargs={"passive_deletes": True})
    occlusal_analyses: "OcclusalAnalysis" = Relationship(back_populates="chart", sa_relationship_kwargs={"passive_deletes": True})
    images: list["ImageManagement"] = Relationship(back_populates="chart")


class DentalChartCreate(DentalChartBase):
    pass


class DentalChartUpdate(SQLModel):
    patient_id: uuid.UUID | None = None
    dentist_id: uuid.UUID | None = None
    record_date: date | None = None
    
