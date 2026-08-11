import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.ai_detection_analysis import AIDetectionAnalysis

# condition/bbox are JSONB so the AI model can return either a simple label
# (e.g. "CARIES") or a richer structure (e.g. {"label": "CARIES", "score": ..})
JSONValue = dict | list | str


class AIDetectionResultBase(SQLModel):
    analysis_id: uuid.UUID = Field(foreign_key="ai_detection_analysis.analysis_id")
    tooth_number: int
    condition: JSONValue = Field(sa_column=Column(JSONB, nullable=False))
    confidence: float
    bbox: JSONValue = Field(sa_column=Column(JSONB, nullable=False))


class AIDetectionResult(AIDetectionResultBase, table=True):
    __tablename__ = "ai_detection_results"

    result_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    analysis: "AIDetectionAnalysis" = Relationship(back_populates="results")


class AIDetectionResultCreate(SQLModel):
    analysis_id: uuid.UUID
    tooth_number: int
    condition: JSONValue
    confidence: float
    bbox: JSONValue


class AIDetectionResultUpdate(SQLModel):
    tooth_number: int | None = None
    condition: JSONValue | None = None
    confidence: float | None = None
    bbox: JSONValue | None = None


class AIDetectionResultRead(SQLModel):
    result_id: uuid.UUID
    tooth_number: int
    condition: JSONValue
    confidence: float
    bbox: JSONValue
