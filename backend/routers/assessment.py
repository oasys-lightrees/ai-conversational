"""Assessment endpoints: start, get, delete."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.assessment import (
    AssessmentResponse,
    StartAssessmentRequest,
    StartAssessmentResponse,
)

router = APIRouter(prefix="/assessment", tags=["assessment"])


@router.post("/start", response_model=StartAssessmentResponse, status_code=status.HTTP_201_CREATED)
def start_assessment(
    _: StartAssessmentRequest | None = None,
    db: Session = Depends(get_db),
) -> StartAssessmentResponse:
    """Create a new assessment session. TODO: implement via AssessmentService."""
    raise NotImplementedError


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: uuid.UUID, db: Session = Depends(get_db)) -> AssessmentResponse:
    """Return all assessment data collected so far. TODO: implement."""
    raise NotImplementedError


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assessment(assessment_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    """Delete or archive an assessment. TODO: implement."""
    raise NotImplementedError
