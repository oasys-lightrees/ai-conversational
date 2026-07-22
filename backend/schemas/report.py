"""Request/response schemas for report endpoints."""

from __future__ import annotations

import uuid

from pydantic import BaseModel

from backend.models.enums import RecommendationPriority


class GenerateReportRequest(BaseModel):
    assessment_id: uuid.UUID


class GenerateReportResponse(BaseModel):
    report_id: uuid.UUID
    status: str = "GENERATED"


class RecommendationResponse(BaseModel):
    title: str
    description: str | None = None
    priority: RecommendationPriority
    estimated_impact: str | None = None


class ReportResponse(BaseModel):
    report_id: uuid.UUID
    executive_summary: str | None = None
    business_analysis: str | None = None
    operational_analysis: str | None = None
    technology_analysis: str | None = None
    ai_readiness: str | None = None
    recommendations_summary: str | None = None
    next_steps: str | None = None
    recommendations: list[RecommendationResponse] = []
