import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel , UniqueConstraint

from app.models.enums import CariesType, SurfaceEnum

if TYPE_CHECKING:
    from app.models.tooth import Tooth


class ToothSurface(SQLModel, table=True):
    __tablename__ = "tooth_surface"
    __table_args__ = (
        UniqueConstraint("tooth_id", "surface", "condition"),
    )

    surface_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tooth_id: uuid.UUID = Field(foreign_key="tooth.tooth_id")
    surface: SurfaceEnum = Field(
        default=None,
        sa_column=Column(SAEnum(SurfaceEnum, name="surface_enum")),
    )
    condition: CariesType = Field(
        default=None,
        sa_column=Column(SAEnum(CariesType, name="caries_type")),
    )

    tooth: "Tooth" = Relationship(back_populates="surfaces")
    

