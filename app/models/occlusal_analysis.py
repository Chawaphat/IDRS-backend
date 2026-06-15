import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import MolarType, LateralDirectionType

if TYPE_CHECKING:
    from app.models.dental_chart import DentalChart
    from app.models.occlusal_contact import OcclusalContact


class OcclusalAnalysisBase(SQLModel):
    right_molar: MolarType | None = None
    left_molar: MolarType | None = None
    overlap_horizontal: float | None = None
    overlap_vertical: float | None = None
    anterior_slide: float | None = None
    lateral_slide: float | None = None
    canine_right: MolarType | None = None
    canine_left: MolarType | None = None
    lateral_direction: LateralDirectionType | None = None
    note: str | None = None

class OcclusalAnalysis(OcclusalAnalysisBase, table=True):
    __tablename__ = "occlusal_analysis"

    occlusal_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chart_id: uuid.UUID = Field(foreign_key="dental_charts.chart_id")
    
    right_molar: MolarType | None = Field(
        default=None,
        sa_column=Column(SAEnum(MolarType, name="molar_type")),
    )
    left_molar: MolarType | None = Field(
        default=None,
        sa_column=Column(SAEnum(MolarType, name="molar_type")),
    )
    canine_right: MolarType | None = Field(
        default=None,
        sa_column=Column(SAEnum(MolarType, name="canine_right_type")),
    )
    canine_left: MolarType | None = Field(
        default=None,
        sa_column=Column(SAEnum(MolarType, name="canine_left_type")),
    )
    lateral_direction: LateralDirectionType | None = Field(
        default=None,
        sa_column=Column(SAEnum(LateralDirectionType, name="lateral_direction_type")),
    )
    
    chart: "DentalChart" = Relationship(back_populates="occlusal_analyses")
    contacts: list["OcclusalContact"] = Relationship(back_populates="occlusal_analysis")


class OcclusalAnalysisCreate(OcclusalAnalysisBase):
    pass


class OcclusalAnalysisUpdate(SQLModel):
    right_molar: MolarType | None = None
    left_molar: MolarType | None = None
    overlap_horizontal: float | None = None
    overlap_vertical: float | None = None
    anterior_slide: float | None = None
    lateral_slide: float | None = None
    canine_right: MolarType | None = None
    canine_left: MolarType | None = None
    lateral_direction: LateralDirectionType | None = None
    note: str | None = None
