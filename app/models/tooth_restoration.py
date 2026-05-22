import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.tooth_record import ToothRecord

from app.models.enums import RestorationTypeEnum, RestorationMaterialEnum, PostTypeEnum

class ToothRestoration(SQLModel, table=True):
    __tablename__ = "tooth_restoration"

    restoration_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tooth_id: uuid.UUID = Field(
        foreign_key="tooth_record.tooth_id",
        unique=True
    )
    restoration_type: RestorationTypeEnum
    material: Optional[RestorationMaterialEnum] = None
    post_type: Optional[PostTypeEnum] = None
    note: Optional[str] = None
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    tooth: "ToothRecord" = Relationship(back_populates="restorations")
