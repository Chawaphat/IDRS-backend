from datetime import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.dental_chart import DentalChart


class ProfileBase(SQLModel):
    license_id: str | None = Field(default=None, max_length=50)
    full_name: str = Field(max_length=255)
    role: UserRole = Field(
        default=UserRole.dentist,
        sa_column=Column(SAEnum(UserRole, name="user_role"), nullable=False),
    )
    phone: str | None = Field(default=None, max_length=15)


class Profile(ProfileBase, table=True):
    __tablename__ = "profiles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )

    dental_charts: list["DentalChart"] = Relationship(back_populates="dentist")


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(SQLModel):
    license_id: str | None = None
    full_name: str | None = None
    role: UserRole | None = None
    phone: str | None = None
