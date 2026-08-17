import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class AIDetectionAnalysisBase(SQLModel):
    image_id: uuid.UUID = Field(foreign_key="image_management.image_id")
    model_name: str
    model_version: str


class AIDetectionAnalysis(AIDetectionAnalysisBase, table=True):
    __tablename__ = "ai_detection_analysis"

    analysis_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: date = Field(default_factory=date.today)
    # Full raw payload returned by the AI model for this run — image path,
    # image_size, every finding (detections[]) and the full per-tooth
    # breakdown incl. healthy teeth (teeth[]). This is the single source of
    # truth for the analysis result; there is no separate per-tooth table.
    detection_data: dict = Field(sa_column=Column(JSONB, nullable=False))


class AIDetectionAnalysisCreate(SQLModel):
    image_id: uuid.UUID
    model_name: Optional[str] = None
    model_version: Optional[str] = None


class AIDetectionAnalysisUpdate(SQLModel):
    image_id: uuid.UUID | None = None
    model_name: str | None = None
    model_version: str | None = None


class AIDetectionAnalysisRead(SQLModel):
    analysis_id: uuid.UUID
    image_id: uuid.UUID
    model_name: str
    model_version: str
    detection_data: dict
