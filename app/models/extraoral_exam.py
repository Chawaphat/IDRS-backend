import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, Column, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import (
    FacialProfileType,
    FacialSymmetryType,
    HabitType,
    JawDeviationType,
    JointPainType,
    JointSoundType,
)

if TYPE_CHECKING:
    from app.models.dental_chart import DentalChart


class ExtraoralExamBase(SQLModel):
    facial_symmetry: FacialSymmetryType 
    facial_profile: FacialProfileType 
    muscle_pain: dict | list | None = None
    joint_pain: list[JointPainType] | None = None
    joint_sound: JointSoundType | None = None
    jaw_deviation: JawDeviationType | None = None
    has_limited_opening: bool | None = None
    mouth_opening_mm: int | None = None
    note: str | None = None
    has_limited_movement: bool | None = None
    specify_movement_detail: str | None = None
    parafunctional_habit: list[HabitType] | None = None
    parafunctional_habit_other: str | None = None
    factors_affecting_tooth_wear: dict | list | None = None


class ExtraoralExam(ExtraoralExamBase, table=True):
    __tablename__ = "extraoral_exams"

    exam_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chart_id: uuid.UUID = Field(foreign_key="dental_charts.chart_id", unique=True)
    chart: "DentalChart" = Relationship()

    facial_symmetry: FacialSymmetryType = Field(
        sa_column=Column(SAEnum(FacialSymmetryType, name="facial_symmetry_type"), nullable=False)
    )

    facial_profile: FacialProfileType = Field(
        sa_column=Column(SAEnum(FacialProfileType, name="facial_profile_type"), nullable=False)
    )
    muscle_pain: dict | list | None = Field(default=None, sa_column=Column(JSONB))
    joint_pain: list[JointPainType] | None = Field(
        default=None,
        sa_column=Column(ARRAY(SAEnum(JointPainType, name="joint_pain_type"))),
    )
    joint_sound: JointSoundType | None = Field(
        default=None,
        sa_column=Column(SAEnum(JointSoundType, name="joint_sound_type")),
    )
    jaw_deviation: JawDeviationType | None = Field(
        default=None,
        sa_column=Column(SAEnum(JawDeviationType, name="jaw_deviation_type")),
    )
    parafunctional_habit: list[HabitType] | None = Field(
        default=None,
        sa_column=Column(ARRAY(SAEnum(HabitType, name="habit_type"))),
    )
    factors_affecting_tooth_wear: dict | list | None = Field(default=None, sa_column=Column(JSONB))

    
class ExtraoralExamCreate(ExtraoralExamBase):
    pass


class ExtraoralExamUpdate(SQLModel):
    facial_symmetry: FacialSymmetryType | None = None
    facial_profile: FacialProfileType | None = None
    muscle_pain: dict | list | None = None
    joint_pain: list[JointPainType] | None = None
    joint_sound: JointSoundType | None = None
    jaw_deviation: JawDeviationType | None = None
    has_limited_opening: bool | None = None
    mouth_opening_mm: int | None = None
    has_limited_movement: bool | None = None
    specify_movement_detail: str | None = None
    parafunctional_habit: list[HabitType] | None = None
    parafunctional_habit_other: str | None = None
    factors_affecting_tooth_wear: dict | list | None = None
    note: str | None = None
