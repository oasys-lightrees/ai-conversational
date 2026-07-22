"""Request/response schemas for assessment endpoints."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel

from backend.models.enums import AssessmentStatus


class StartAssessmentRequest(BaseModel):
    """POST /assessment/start — no body required."""


class StartAssessmentResponse(BaseModel):
    assessment_id: uuid.UUID
    status: AssessmentStatus
    message: str


class AssessmentResponse(BaseModel):
    assessment_id: uuid.UUID
    status: AssessmentStatus
    completion_percentage: int
    assessment_data: dict[str, Any] = {}
