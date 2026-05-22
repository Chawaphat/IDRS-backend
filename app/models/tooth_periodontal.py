import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.tooth_record import ToothRecord

from app.models.enums import MobilityGradeEnum

class ToothPeriodontal(SQLModel, table=True):
    __tablename__ = "tooth_periodontal"

    periodontal_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tooth_id: uuid.UUID = Field(
        foreign_key="tooth_record.tooth_id",
        unique=True
    )
    mobility_grade: Optional[MobilityGradeEnum] = None
    recession_mm: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    note: Optional[str] = Field(default=None, max_length=255)
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    tooth: "ToothRecord" = Relationship(back_populates="periodontal")
