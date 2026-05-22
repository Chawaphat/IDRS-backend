import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.dental_status import DentalStatus
    from app.models.tooth_edentulous import ToothEdentulous
    from app.models.tooth_caries import ToothCaries
    from app.models.tooth_filling import ToothFilling
    from app.models.tooth_periodontal import ToothPeriodontal
    from app.models.tooth_vitality import ToothVitality
    from app.models.tooth_restoration import ToothRestoration
    from app.models.tooth_implant import ToothImplant

from app.models.enums import ToothTypeEnum

class ToothRecord(SQLModel, table=True):
    __tablename__ = "tooth_record"

    tooth_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status_id: uuid.UUID = Field(foreign_key="dental_status.status_id")
    tooth_number: int
    tooth_type: ToothTypeEnum
    note: Optional[str] = None
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # Relationships
    status_record: "DentalStatus" = Relationship(back_populates="teeth")

    # 1-to-1
    edentulous: Optional["ToothEdentulous"] = Relationship(
        back_populates="tooth",
        sa_relationship_kwargs={"passive_deletes": True, "uselist": False}
    )
    periodontal: Optional["ToothPeriodontal"] = Relationship(
        back_populates="tooth",
        sa_relationship_kwargs={"passive_deletes": True, "uselist": False}
    )
    vitality: Optional["ToothVitality"] = Relationship(
        back_populates="tooth",
        sa_relationship_kwargs={"passive_deletes": True, "uselist": False}
    )
    restorations: Optional["ToothRestoration"] = Relationship(
        back_populates="tooth",
        sa_relationship_kwargs={"passive_deletes": True, "uselist": False}
    )
    implant: Optional["ToothImplant"] = Relationship(
        back_populates="tooth",
        sa_relationship_kwargs={"passive_deletes": True, "uselist": False}
    )
    

    # 1-to-many
    caries: list["ToothCaries"] = Relationship(
        back_populates="tooth",
        sa_relationship_kwargs={"passive_deletes": True}
    )
    fillings: list["ToothFilling"] = Relationship(
        back_populates="tooth",
        sa_relationship_kwargs={"passive_deletes": True}
    )
    