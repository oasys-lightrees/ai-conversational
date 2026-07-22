"""Report endpoints: generate and fetch."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.report import (
    GenerateReportRequest,
    GenerateReportResponse,
    RecommendationResponse,
    ReportResponse,
)
from backend.services.assessment_service import AssessmentNotFound
from backend.services.report_service import AssessmentNotCompleted, ReportService

router = APIRouter(prefix="/report", tags=["report"])


@router.post("/generate", response_model=GenerateReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    request: GenerateReportRequest, db: Session = Depends(get_db)
) -> GenerateReportResponse:
    """Generate the final assessment report."""
    try:
        report = ReportService(db).generate(request.assessment_id)
    except AssessmentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    except AssessmentNotCompleted:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Assessment is not completed.",
        )
    return GenerateReportResponse(report_id=report.id)


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: uuid.UUID, db: Session = Depends(get_db)) -> ReportResponse:
    """Return a generated report."""
    report = ReportService(db).get(report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    return ReportResponse(
        report_id=report.id,
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
