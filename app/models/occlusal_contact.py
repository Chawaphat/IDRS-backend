import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import ContactType

if TYPE_CHECKING:
    from app.models.occlusal_analysis import OcclusalAnalysis


class OcclusalContact(SQLModel, table=True):
    __tablename__ = "occlusal_contacts"

    contact_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    occlusal_id: uuid.UUID = Field(foreign_key="occlusal_analysis.occlusal_id")
    contact_type: ContactType = Field(
        sa_column=Column(SAEnum(ContactType, name="contact_type")),
    )
    upper_tooth: int 
    lower_tooth: int 

    occlusal_analysis: "OcclusalAnalysis" = Relationship(back_populates="contacts")


class OcclusalContactCreate(SQLModel):
    contact_type: ContactType 
    upper_tooth: int 
    lower_tooth: int 


class OcclusalContactUpdate(SQLModel):
    occlusal_id: uuid.UUID | None = None
    contact_type: ContactType | None = None
    upper_tooth: int | None = None
    lower_tooth: int | None = None
