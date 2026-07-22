"""Report and Recommendation ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.enums import RecommendationPriority


class Report(Base):
    """Generated business assessment report."""

    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), unique=True
    )
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    business_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    operational_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    technology_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_readiness: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_steps: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    assessment: Mapped["Assessment"] = relationship(back_populates="report")  # noqa: F821
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )


class Recommendation(Base):
    """A single structured recommendation attached to a report."""

    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[RecommendationPriority] = mapped_column(
        Enum(RecommendationPriority), default=RecommendationPriority.MEDIUM, nullable=False
    )
    estimated_impact: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    report: Mapped["Report"] = relationship(back_populates="recommendations")
