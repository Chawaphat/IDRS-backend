import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, Column, Enum as SAEnum, Integer
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import BiteType, FacialConditionType

if TYPE_CHECKING:
    from app.models.dental_chart import DentalChart


class VdoEvaluationBase(SQLModel):
    facial_soft_tissue: list[FacialConditionType] | None = None
    closest_speaking: float | None = None
    free_way_space: float | None = None
    bite_type: BiteType | None = None
    reference_teeth: list[int] | None = None


class VdoEvaluation(VdoEvaluationBase, table=True):
    __tablename__ = "vdo_evaluations"

    vdo_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chart_id: uuid.UUID = Field(foreign_key="dental_charts.chart_id", unique=True)

    chart: "DentalChart" = Relationship(back_populates="vdo_evaluations")

    facial_soft_tissue: list[FacialConditionType] | None = Field(
        default=None,
        sa_column=Column(ARRAY(SAEnum(FacialConditionType, name="facial_condition_type"))),
    )

    bite_type: BiteType | None = Field(
        default=None,
        sa_column=Column(SAEnum(BiteType, name="bite_type")),
    )
    reference_teeth: list[int] | None = Field(default=None, sa_column=Column(ARRAY(Integer)))
    
class VdoEvaluationCreate(VdoEvaluationBase):
    pass


class VdoEvaluationUpdate(SQLModel):
    facial_soft_tissue: list[FacialConditionType] | None = None
    closest_speaking: float | None = None
    free_way_space: float | None = None
    bite_type: BiteType | None = None
    reference_teeth: list[int] | None = None
