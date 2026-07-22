"""Assessment and AssessmentData ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.enums import (
    AssessmentStatus,
    BusinessStage,
    OwnershipType,
    ProcessType,
    PropertyType,
)


class Assessment(Base):
    """Metadata about a single assessment session."""

    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    status: Mapped[AssessmentStatus] = mapped_column(
        Enum(AssessmentStatus), default=AssessmentStatus.IN_PROGRESS, nullable=False
    )
    completion_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    data: Mapped["AssessmentData"] = relationship(
        back_populates="assessment", uselist=False, cascade="all, delete-orphan"
    )
    conversations: Mapped[list["Conversation"]] = relationship(  # noqa: F821
        back_populates="assessment", cascade="all, delete-orphan"
    )
    report: Mapped["Report | None"] = relationship(  # noqa: F821
        back_populates="assessment", uselist=False, cascade="all, delete-orphan"
    )


class AssessmentData(Base):
    """Business information collected during an assessment."""

    __tablename__ = "assessment_data"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), unique=True
    )

    # Property profile
    property_name: Mapped[str | None] = mapped_column(String, nullable=True)
    property_type: Mapped[PropertyType | None] = mapped_column(Enum(PropertyType), nullable=True)
    property_location: Mapped[str | None] = mapped_column(String, nullable=True)
    ownership_type: Mapped[OwnershipType | None] = mapped_column(Enum(OwnershipType), nullable=True)
    total_units: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Business stage & performance
    business_stage: Mapped[BusinessStage | None] = mapped_column(Enum(BusinessStage), nullable=True)
    occupancy_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    monthly_revenue: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    average_room_rate: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)

    # Operations
    staff_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    check_in_process: Mapped[ProcessType | None] = mapped_column(Enum(ProcessType), nullable=True)
    housekeeping_process: Mapped[ProcessType | None] = mapped_column(Enum(ProcessType), nullable=True)
    maintenance_process: Mapped[ProcessType | None] = mapped_column(Enum(ProcessType), nullable=True)
    complaint_handling: Mapped[ProcessType | None] = mapped_column(Enum(ProcessType), nullable=True)

    # Technology
    uses_pms: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    pms_name: Mapped[str | None] = mapped_column(String, nullable=True)
    accounting_system: Mapped[str | None] = mapped_column(String, nullable=True)
    booking_platforms: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    communication_channels: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Pain points & goals
    pain_points: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    business_goals: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # AI readiness
    ai_readiness_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    assessment: Mapped["Assessment"] = relationship(back_populates="data")
