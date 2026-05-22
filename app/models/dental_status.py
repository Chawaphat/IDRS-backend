from datetime import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.dental_chart import DentalChart
    from app.models.tooth_record import ToothRecord


class DentalStatus(SQLModel, table=True):
    __tablename__ = "dental_status"

    status_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chart_id: uuid.UUID = Field(foreign_key="dental_charts.chart_id")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )

    chart: "DentalChart" = Relationship(back_populates="dental_status_records")
    teeth: list["ToothRecord"] = Relationship(back_populates="status_record", sa_relationship_kwargs={"passive_deletes": True})

