from datetime import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
# SQLMODEL = base class
# Field define column/ validation
# Relationship define relationship กับ table อื่นๆ
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.dental_chart import DentalChart

# Base class คือ - reuse filed ที่ใช้บ่อยๆ ในการสร้าง model ต่างๆ เช่น create, update, table model เพื่อให้โค้ดสะอาดและลดการซ้ำซ้อนในการประกาศ field ต่างๆ 
# - ไม่ใช้ table เพราะเป็นแค่ base class ไม่ได้สร้าง table จริงๆ ใน database
class PatientBase(SQLModel):
    hn_number: str = Field(max_length=20, sa_column_kwargs={"unique": True})    
    name: str = Field(max_length=255)
    sex: str | None = Field(default=None, max_length=10)
    age: int | None = None
    phone: str | None = Field(default=None, max_length=15)
    allergy: str | None = Field(default=None, max_length=20)

# Patient model คือ - ใช้สำหรับสร้าง table จริงๆ ใน database และมีความสัมพันธ์กับ dental_chart ผ่าน relationship 
class Patient(PatientBase, table=True):
    # map กับ table ใน database ชื่อ patients
    __tablename__ = "patients"

    patient_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )

    # relationship กับ dental_chart คือ - 1 คนไข้สามารถมีหลาย dental_chart ได้ แต่ละ dental_chart จะมี patient_id เป็น foreign key ที่เชื่อมกับ patient_id ใน table patients
    # back_populates คือ - ใช้เพื่อบอกว่า relationship นี้เชื่อมกับ field dental_charts ใน model DentalChart ซึ่งจะทำให้สามารถเข้าถึง dental_charts ของ patient ได้ง่ายๆ ผ่าน patient.dental_charts
    # @OneToMany 
    dental_charts: list["DentalChart"] = Relationship(back_populates="patient")

# For post request body
class PatientCreate(PatientBase):
    pass

# For put request body - ใช้สำหรับ update ข้อมูลคนไข้ โดย field ต่างๆ เป็น optional เพราะไม่จำเป็นต้องอัพเดททุก field ในครั้งเดียว
class PatientUpdate(SQLModel):
    hn_number: str | None = None
    name: str | None = None
    sex: str | None = None
    age: int | None = None
    phone: str | None = None
    allergy: str | None = None
