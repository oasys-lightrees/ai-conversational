"""Assessment endpoints: start, get, delete."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.assessment import (
    AssessmentResponse,
    StartAssessmentRequest,
    StartAssessmentResponse,
)
from backend.services.assessment_service import AssessmentNotFound, AssessmentService
from backend.services.template_service import TemplateNotFound, TemplateService

router = APIRouter(prefix="/assessment", tags=["assessment"])


@router.post("/start", response_model=StartAssessmentResponse, status_code=status.HTTP_201_CREATED)
def start_assessment(
    request: StartAssessmentRequest | None = None,
    db: Session = Depends(get_db),
) -> StartAssessmentResponse:
    """Create a new assessment session, optionally from a chosen template."""
    template_id = request.template_id if request else None
    try:
        resolved_id, config = TemplateService(db).resolve_for_start(template_id)
    except TemplateNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")

    assessment = AssessmentService(db, config=config).create(template_id=resolved_id)
    return StartAssessmentResponse(
        assessment_id=assessment.id,
        status=assessment.status,
        message="Assessment started.",
    )


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: uuid.UUID, db: Session = Depends(get_db)) -> AssessmentResponse:
    """Return all assessment data collected so far."""
    service = AssessmentService(db)
    assessment = service.get(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    return AssessmentResponse(
        assessment_id=assessment.id,
        status=assessment.status,
        completion_percentage=assessment.completion_percentage,
        assessment_data=service.to_state_dict(assessment.data),
    )


@router.delete(
    "/{assessment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
def delete_assessment(assessment_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    """Delete an assessment."""
    try:
        AssessmentService(db).delete(assessment_id)
    except AssessmentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
