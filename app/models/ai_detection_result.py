import uuid

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class AIDetectionResult(SQLModel, table=True):
    __tablename__ = "ai_detection_results"

    result_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    image_id: uuid.UUID = Field(foreign_key="image_management.image_id")
    detection_data: dict | list = Field(sa_column=Column(JSONB, nullable=False))


class AIDetectionResultCreate(SQLModel):
    image_id: uuid.UUID
    detection_data: dict | list


class AIDetectionResultUpdate(SQLModel):
    image_id: uuid.UUID | None = None
    detection_data: dict | list | None = None
