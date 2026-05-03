import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from app.models.dental_status import DentalStatus
    from app.models.tooth_surface import ToothSurface


class Tooth(SQLModel, table=True):
    __tablename__ = "tooth"
    __table_args__ = (
    UniqueConstraint("status_id", "tooth_number"),
    )
    
    tooth_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status_id: uuid.UUID = Field(foreign_key="dental_status.status_id")
    tooth_number: int
    tooth_status: str | None = Field(default=None, max_length=50)
    crown: str | None = Field(default=None, max_length=50)
    tooth_detail: str | None = None
    root_status: str | None = Field(default=None, max_length=50)

    status_record: "DentalStatus" = Relationship(back_populates="teeth")
    surfaces: list["ToothSurface"] = Relationship(back_populates="tooth", sa_relationship_kwargs={"passive_deletes": True})


