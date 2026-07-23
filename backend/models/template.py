"""AssessmentTemplate ORM model — a named, stored PipelineConfig."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class AssessmentTemplate(Base):
    """A reusable pipeline configuration (knowledge, style, language, fields).

    ``config`` holds a serialized ``PipelineConfig``. At ``/assessment/start`` the
    chosen template's config is snapshotted onto the assessment, so in-flight
    assessments are unaffected by later template edits.
    """

    __tablename__ = "assessment_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
