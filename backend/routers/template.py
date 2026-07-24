"""Template endpoints: list and fetch seeded pipeline templates."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.pipeline.config import PipelineConfig
from backend.schemas.template import TemplateDetail, TemplateSummary
from backend.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[TemplateSummary])
def list_templates(db: Session = Depends(get_db)) -> list[TemplateSummary]:
    """List available assessment templates."""
    return [
        TemplateSummary(
            id=t.id,
            name=t.name,
            description=t.description,
            language=str(t.config.get("language", "id")),
            is_default=t.is_default,
        )
        for t in TemplateService(db).list()
    ]


@router.get("/{template_id}", response_model=TemplateDetail)
def get_template(template_id: uuid.UUID, db: Session = Depends(get_db)) -> TemplateDetail:
    """Return a template's full config."""
    template = TemplateService(db).get(template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")
    return TemplateDetail(
        id=template.id,
        name=template.name,
        description=template.description,
        is_default=template.is_default,
        config=PipelineConfig(**template.config),
    )
