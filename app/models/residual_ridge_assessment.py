import uuid
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import (
    RidgeHeightType,
    RidgeWidthType,
    JawSizeType,
    RidgeShapeType,
    RidgeRelationType,
    RidgeParallelismType,
    InterridgeSpaceType,
    ArchFormType,
    PalatalVaultType,
    PalatalThroatFormType,
    TongueSizeType,
    TonguePositionType,
    SalivaAmountType,
    SalivaConsistencyType,
    LipMobilityType,
    FacialMuscleToneType,
    MentalAttitudeType,
)

if TYPE_CHECKING:
    from app.models.dental_chart import DentalChart


class ResidualRidgeAssessmentBase(SQLModel):
    ridge_height: RidgeHeightType | None = Field(
        default=None, sa_column=Column(SAEnum(RidgeHeightType, name="ridge_height_type"))
    )
    ridge_width: RidgeWidthType | None = Field(
        default=None, sa_column=Column(SAEnum(RidgeWidthType, name="ridge_width_type"))
    )
    jaw_size: JawSizeType | None = Field(
        default=None, sa_column=Column(SAEnum(JawSizeType, name="jaw_size_type"))
    )
    ridge_shape_upper: RidgeShapeType | None = Field(
        default=None, sa_column=Column(SAEnum(RidgeShapeType, name="ridge_shape_upper_type"))
    )
    ridge_shape_lower: RidgeShapeType | None = Field(
        default=None, sa_column=Column(SAEnum(RidgeShapeType, name="ridge_shape_lower_type"))
    )
    ridge_relation: RidgeRelationType | None = Field(
        default=None, sa_column=Column(SAEnum(RidgeRelationType, name="ridge_relation_type"))
    )
    ridge_parallelism: RidgeParallelismType | None = Field(
        default=None, sa_column=Column(SAEnum(RidgeParallelismType, name="ridge_parallelism_type"))
    )
    interridge_space: InterridgeSpaceType | None = Field(
        default=None, sa_column=Column(SAEnum(InterridgeSpaceType, name="interridge_space_type"))
    )
    lower_arch_form: ArchFormType | None = Field(
        default=None, sa_column=Column(SAEnum(ArchFormType, name="arch_form_type"))
    )
    palatal_vault: PalatalVaultType | None = Field(
        default=None, sa_column=Column(SAEnum(PalatalVaultType, name="palatal_vault_type"))
    )
    palatal_throat_form: PalatalThroatFormType | None = Field(
        default=None, sa_column=Column(SAEnum(PalatalThroatFormType, name="palatal_throat_form_type"))
    )

    freenum_attachment: dict | list | None = Field(default=None, sa_column=Column(JSONB))
    ridge_deformity: dict | list | None = Field(default=None, sa_column=Column(JSONB))
    torus_palatinus: dict | list | None = Field(default=None, sa_column=Column(JSONB))

    tongue_size: TongueSizeType | None = Field(
        default=None, sa_column=Column(SAEnum(TongueSizeType, name="tongue_size_type"))
    )
    tongue_position: TonguePositionType | None = Field(
        default=None, sa_column=Column(SAEnum(TonguePositionType, name="tongue_position_type"))
    )
    saliva_amount: SalivaAmountType | None = Field(
        default=None, sa_column=Column(SAEnum(SalivaAmountType, name="saliva_amount_type"))
    )
    saliva_consistency: SalivaConsistencyType | None = Field(
        default=None, sa_column=Column(SAEnum(SalivaConsistencyType, name="saliva_consistency_type"))
    )
    lip_mobility: LipMobilityType | None = Field(
        default=None, sa_column=Column(SAEnum(LipMobilityType, name="lip_mobility_type"))
    )
    facial_muscle_tone: FacialMuscleToneType | None = Field(
        default=None, sa_column=Column(SAEnum(FacialMuscleToneType, name="facial_muscle_tone_type"))
    )
    mental_attitude: MentalAttitudeType | None = Field(
        default=None, sa_column=Column(SAEnum(MentalAttitudeType, name="mental_attitude_type"))
    )


class ResidualRidgeAssessment(ResidualRidgeAssessmentBase, table=True):
    __tablename__ = "residual_ridge_assessment"

    assessment_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chart_id: uuid.UUID = Field(foreign_key="dental_charts.chart_id", unique=True)
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # 1-to-1 relationship to DentalChart (assuming you'll add 'residual_ridge_assessment' back_populates in chart model)
    chart: "DentalChart" = Relationship(back_populates="residual_ridge_assessment")


class ResidualRidgeAssessmentCreate(ResidualRidgeAssessmentBase):
    pass


class ResidualRidgeAssessmentUpdate(SQLModel):
    ridge_height: RidgeHeightType | None = None
    ridge_width: RidgeWidthType | None = None
    jaw_size: JawSizeType | None = None
    ridge_shape_upper: RidgeShapeType | None = None
    ridge_shape_lower: RidgeShapeType | None = None
    ridge_relation: RidgeRelationType | None = None
    ridge_parallelism: RidgeParallelismType | None = None
    interridge_space: InterridgeSpaceType | None = None
    lower_arch_form: ArchFormType | None = None
    palatal_vault: PalatalVaultType | None = None
    palatal_throat_form: PalatalThroatFormType | None = None
    freenum_attachment: dict | list | None = None
    ridge_deformity: dict | list | None = None
    torus_palatinus: dict | list | None = None
    tongue_size: TongueSizeType | None = None
    tongue_position: TonguePositionType | None = None
    saliva_amount: SalivaAmountType | None = None
    saliva_consistency: SalivaConsistencyType | None = None
    lip_mobility: LipMobilityType | None = None
    facial_muscle_tone: FacialMuscleToneType | None = None
    mental_attitude: MentalAttitudeType | None = None
