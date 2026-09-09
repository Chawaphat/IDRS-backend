import os
from datetime import datetime
import uuid
from typing import TYPE_CHECKING

from pydantic import field_validator
from sqlalchemy import Column, DateTime, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import ImageCategory

if TYPE_CHECKING:
    from app.models.dental_chart import DentalChart

# Upload constraints enforced on image record creation (UTC-36).
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

class ImageManagementBase(SQLModel):
    image_type: ImageCategory 
    image_url: str | None = None
    image_file: str | None = None
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
    # Size of the uploaded file in bytes. Upload metadata only — validated
    # here, not persisted to the image_management table.
    file_size: int | None = None

    @field_validator("image_file")
    @classmethod
    def _validate_image_file_extension(cls, v: str | None) -> str | None:
        if v is None:
            return v
        ext = os.path.splitext(v)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValueError(
                f"'{ext or v}' is not a supported image file type; "
                f"supported types: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"
            )
        return v

    @field_validator("file_size")
    @classmethod
    def _validate_file_size(cls, v: int | None) -> int | None:
        if v is not None and v > MAX_IMAGE_FILE_SIZE_BYTES:
            raise ValueError("file size exceeds the 10 MB limit")
        return v


class ImageManagementUpdate(SQLModel):
    image_type: ImageCategory | None = None
    image_url: str | None = None
    image_file: str | None = None
    description: str | None = None
