"""Request/response schemas for the admin API."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from backend.models.enums import AssessmentStatus
from backend.pipeline.config import PipelineConfig
from backend.schemas.chat import ConversationMessage


# --- Templates ---------------------------------------------------------------


class TemplateWrite(BaseModel):
    name: str
    description: str | None = None
    is_default: bool = False
    config: PipelineConfig


# --- Assessments -------------------------------------------------------------


class AssessmentListItem(BaseModel):
    assessment_id: uuid.UUID
    status: AssessmentStatus
    completion_percentage: int
    template_id: uuid.UUID | None = None
    created_at: datetime
    completed_at: datetime | None = None


class PaginatedAssessments(BaseModel):
    items: list[AssessmentListItem]
    total: int
    page: int
    page_size: int


class AssessmentDetail(BaseModel):
    assessment_id: uuid.UUID
    status: AssessmentStatus
    completion_percentage: int
    template_id: uuid.UUID | None = None
    created_at: datetime
    completed_at: datetime | None = None
    assessment_data: dict = {}
    conversation: list[ConversationMessage] = []


# --- Metrics -----------------------------------------------------------------


class NamedCount(BaseModel):
    key: str
    count: int


class Metrics(BaseModel):
    total_assessments: int
    by_status: dict[str, int]
    completion_rate: float  # completed / total
    average_completion: float
    by_property_type: list[NamedCount]
    by_business_stage: list[NamedCount]
