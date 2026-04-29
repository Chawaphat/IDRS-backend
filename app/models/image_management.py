from datetime import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import ImageCategory

if TYPE_CHECKING:
    from app.models.dental_chart import DentalChart

class ImageManagementBase(SQLModel):
    image_type: ImageCategory 
    image_url: str
    image_file: str
    description: str | None = None


class ImageManagement(ImageManagementBase, table=True):
    __tablename__ = "image_management"

    image_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chart_id: uuid.UUID = Field(foreign_key="dental_charts.chart_id")
    uploaded_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )
    image_type: ImageCategory = Field(
        default=None,
        sa_column=Column(SAEnum(ImageCategory, name="image_category")),
    )
    chart: "DentalChart" = Relationship(back_populates="images")


class ImageManagementCreate(ImageManagementBase):
    pass


class ImageManagementUpdate(SQLModel):
    image_type: ImageCategory | None = None
    image_url: str | None = None
    image_file: str | None = None
    description: str | None = None
