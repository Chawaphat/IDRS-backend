import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.tooth_record import ToothRecord

from app.models.enums import FillingMaterialEnum

class ToothFilling(SQLModel, table=True):
    __tablename__ = "tooth_filling"

    filling_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tooth_id: uuid.UUID = Field(foreign_key="tooth_record.tooth_id")
    
    surfaces: List[str] = Field(sa_column=Column(JSONB, nullable=False))
    material: FillingMaterialEnum
    size_mm: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    note: Optional[str] = None
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    tooth: "ToothRecord" = Relationship(back_populates="fillings")
