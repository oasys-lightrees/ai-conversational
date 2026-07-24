"""Admin template CRUD."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.pipeline.config import PipelineConfig
from backend.schemas.admin import TemplateWrite
from backend.schemas.template import TemplateDetail, TemplateSummary
from backend.services.template_service import (
    DuplicateTemplateName,
    TemplateInUse,
    TemplateInvalid,
    TemplateNotFound,
    TemplateService,
)

router = APIRouter(prefix="/templates", tags=["admin:templates"])


def _detail(template) -> TemplateDetail:
    return TemplateDetail(
        id=template.id,
        name=template.name,
        description=template.description,
        is_default=template.is_default,
        config=PipelineConfig(**template.config),
    )


@router.get("", response_model=list[TemplateSummary])
def list_templates(db: Session = Depends(get_db)) -> list[TemplateSummary]:
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


@router.post("", response_model=TemplateDetail, status_code=status.HTTP_201_CREATED)
def create_template(body: TemplateWrite, db: Session = Depends(get_db)) -> TemplateDetail:
    try:
        template = TemplateService(db).create(
            body.name, body.description, body.is_default, body.config
        )
    except TemplateInvalid as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except DuplicateTemplateName:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Template name already exists.")
    return _detail(template)


@router.get("/{template_id}", response_model=TemplateDetail)
def get_template(template_id: uuid.UUID, db: Session = Depends(get_db)) -> TemplateDetail:
    template = TemplateService(db).get(template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")
    return _detail(template)


@router.put("/{template_id}", response_model=TemplateDetail)
def update_template(
    template_id: uuid.UUID, body: TemplateWrite, db: Session = Depends(get_db)
) -> TemplateDetail:
    try:
        template = TemplateService(db).update(
            template_id, body.name, body.description, body.is_default, body.config
        )
    except TemplateNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")
    except TemplateInvalid as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except DuplicateTemplateName:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Template name already exists.")
    return _detail(template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_template(template_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        TemplateService(db).delete(template_id)
    except TemplateNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")
    except TemplateInUse:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Template is in use by existing assessments.",
        )


@router.post("/{template_id}/clone", response_model=TemplateDetail, status_code=status.HTTP_201_CREATED)
def clone_template(template_id: uuid.UUID, db: Session = Depends(get_db)) -> TemplateDetail:
    try:
        return _detail(TemplateService(db).clone(template_id))
    except TemplateNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")


@router.post("/{template_id}/default", response_model=TemplateDetail)
def set_default_template(template_id: uuid.UUID, db: Session = Depends(get_db)) -> TemplateDetail:
    try:
        return _detail(TemplateService(db).set_default(template_id))
    except TemplateNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")
