import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.models.ai_detection_result import AIDetectionResultRead

if TYPE_CHECKING:
    from app.models.ai_detection_result import AIDetectionResult


class AIDetectionAnalysisBase(SQLModel):
    image_id: uuid.UUID = Field(foreign_key="image_management.image_id")
    model_name: str
    model_version: str


class AIDetectionAnalysis(AIDetectionAnalysisBase, table=True):
    __tablename__ = "ai_detection_analysis"

    analysis_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: date = Field(default_factory=date.today)

    # 1-to-many: one analysis run produces many per-tooth results
    results: list["AIDetectionResult"] = Relationship(
        back_populates="analysis",
        sa_relationship_kwargs={"passive_deletes": True},
    )


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
    results: list[AIDetectionResultRead] = []
