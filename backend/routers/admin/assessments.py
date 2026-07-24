"""Admin assessments browser — list, detail, delete."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Assessment, Report
from backend.models.enums import AssessmentStatus
from backend.schemas.admin import (
    AssessmentDetail,
    AssessmentListItem,
    PaginatedAssessments,
)
from backend.schemas.report import RecommendationResponse, ReportResponse
from backend.services.assessment_service import AssessmentNotFound, AssessmentService
from backend.services.chat_service import ChatService

router = APIRouter(prefix="/assessments", tags=["admin:assessments"])


@router.get("", response_model=PaginatedAssessments)
def list_assessments(
    db: Session = Depends(get_db),
    status_filter: AssessmentStatus | None = Query(default=None, alias="status"),
    template_id: uuid.UUID | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedAssessments:
    filters = []
    if status_filter is not None:
        filters.append(Assessment.status == status_filter)
    if template_id is not None:
        filters.append(Assessment.template_id == template_id)

    total = db.scalar(select(func.count()).select_from(Assessment).where(*filters)) or 0
    rows = db.scalars(
        select(Assessment)
        .where(*filters)
        .order_by(Assessment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items = [
        AssessmentListItem(
            assessment_id=a.id,
            status=a.status,
            completion_percentage=a.completion_percentage,
            template_id=a.template_id,
            created_at=a.created_at,
            completed_at=a.completed_at,
        )
        for a in rows
    ]
    return PaginatedAssessments(items=items, total=total, page=page, page_size=page_size)


@router.get("/{assessment_id}", response_model=AssessmentDetail)
def get_assessment_detail(
    assessment_id: uuid.UUID, db: Session = Depends(get_db)
) -> AssessmentDetail:
    service = AssessmentService(db)
    assessment = service.get(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")

    report = db.scalar(select(Report).where(Report.assessment_id == assessment_id))
    report_response = None
    if report is not None:
        report_response = ReportResponse(
            report_id=report.id,
            assessment_id=report.assessment_id,
            executive_summary=report.executive_summary,
            business_analysis=report.business_analysis,
            operational_analysis=report.operational_analysis,
            technology_analysis=report.technology_analysis,
            ai_readiness=report.ai_readiness,
            recommendations_summary=report.recommendations_summary,
            next_steps=report.next_steps,
            recommendations=[
                RecommendationResponse(
                    title=rec.title,
                    description=rec.description,
                    priority=rec.priority,
                    estimated_impact=rec.estimated_impact,
                )
                for rec in report.recommendations
            ],
        )

    return AssessmentDetail(
        assessment_id=assessment.id,
        status=assessment.status,
        completion_percentage=assessment.completion_percentage,
        template_id=assessment.template_id,
        created_at=assessment.created_at,
        completed_at=assessment.completed_at,
        assessment_data=service.to_state_dict(assessment.data),
        conversation=ChatService(db).history(assessment_id),
        report=report_response,
    )


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_assessment(assessment_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        AssessmentService(db).delete(assessment_id)
    except AssessmentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
