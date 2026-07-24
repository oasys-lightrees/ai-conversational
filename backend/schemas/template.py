"""Request/response schemas for template endpoints."""

from __future__ import annotations

import uuid

from pydantic import BaseModel

from backend.pipeline.config import PipelineConfig


class TemplateSummary(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    language: str
    is_default: bool


class TemplateDetail(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    is_default: bool
    config: PipelineConfig
