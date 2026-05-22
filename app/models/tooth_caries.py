# tooth_caries.py
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.tooth_record import ToothRecord

from app.models.enums import ToothSurfaceEnum, CariesDepthEnum

class ToothCaries(SQLModel, table=True):
    __tablename__ = "tooth_caries"

    caries_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tooth_id: uuid.UUID = Field(foreign_key="tooth_record.tooth_id")
    surface: ToothSurfaceEnum
    depth: CariesDepthEnum
    note: Optional[str] = None
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    tooth: "ToothRecord" = Relationship(back_populates="caries")