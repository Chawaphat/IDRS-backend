# tooth_vitality.py (1-to-1 pattern)
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.tooth_record import ToothRecord

from app.models.enums import EptResultEnum, RootCanalTreatedEnum

class ToothVitality(SQLModel, table=True):
    __tablename__ = "tooth_vitality"

    vitality_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tooth_id: uuid.UUID = Field(
        foreign_key="tooth_record.tooth_id",
        unique=True   # enforce 1-to-1
    )
    pulp_status: Optional[str] = None
    ept_result: Optional[EptResultEnum] = None
    root_canal_treated: Optional[RootCanalTreatedEnum] = None
    note: Optional[str] = None
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    tooth: "ToothRecord" = Relationship(back_populates="vitality")