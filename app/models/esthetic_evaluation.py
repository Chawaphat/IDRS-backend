import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, Column, Enum as SAEnum, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import (
    LipLengthType,
    LipThicknessType,
    MidlineDiscrepancyType,
    NasolabialAngleType,
    OcclusalPlaneType,
)

if TYPE_CHECKING:
    from app.models.dental_chart import DentalChart


class EstheticEvaluationBase(SQLModel):
    occlusal_plane: OcclusalPlaneType | None = Field(
        default=None,
        sa_column=Column(SAEnum(OcclusalPlaneType, name="occlusal_plane_type")),
    )
    midline_discrepancy: MidlineDiscrepancyType | None = Field(
        default=None,
        sa_column=Column(SAEnum(MidlineDiscrepancyType, name="midline_discrepancy_type")),
    )
    lip_thickness: LipThicknessType | None = Field(
        default=None,
        sa_column=Column(SAEnum(LipThicknessType, name="lip_thickness_type")),
    )
    lip_length: LipLengthType | None = Field(
        default=None,
        sa_column=Column(SAEnum(LipLengthType, name="lip_length_type")),
    )
    upper_tooth_exposure: float | None = None
    lower_tooth_exposure: float | None = None
    midline_shift: float | None = None
    nasolabial_angle: NasolabialAngleType | None = Field(
        default=None,
        sa_column=Column(SAEnum(NasolabialAngleType, name="nasolabial_angle_type")),
    )
    dentofacial_analysis: dict | list | None = Field(default=None, sa_column=Column(JSONB))
    fv_sound: bool | None = None
    closest_speaking: float | None = None
    reference_teeth: list[int] | None = Field(default=None, sa_column=Column(ARRAY(Integer)))
    note: str | None = None


class EstheticEvaluation(EstheticEvaluationBase, table=True):
    __tablename__ = "esthetic_evaluation"

    esthetic_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chart_id: uuid.UUID = Field(foreign_key="dental_charts.chart_id", unique=True)

    chart: "DentalChart" = Relationship(back_populates="esthetic_evaluations")
    

class EstheticEvaluationCreate(EstheticEvaluationBase):
    pass


class EstheticEvaluationUpdate(SQLModel):
    occlusal_plane: OcclusalPlaneType | None = None
    midline_discrepancy: MidlineDiscrepancyType | None = None
    lip_thickness: LipThicknessType | None = None
    lip_length: LipLengthType | None = None
    upper_tooth_exposure: float | None = None
    lower_tooth_exposure: float | None = None
    midline_shift: float | None = None
    nasolabial_angle: NasolabialAngleType | None = None
    dentofacial_analysis: dict | list | None = None
    fv_sound: bool | None = None
    closest_speaking: float | None = None
    reference_teeth: list[int] | None = None
    note: str | None = None
