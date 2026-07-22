"""Report endpoints: generate and fetch."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.report import (
    GenerateReportRequest,
    GenerateReportResponse,
    ReportResponse,
)

router = APIRouter(prefix="/report", tags=["report"])


@router.post("/generate", response_model=GenerateReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    request: GenerateReportRequest, db: Session = Depends(get_db)
) -> GenerateReportResponse:
    """Generate the final assessment report. TODO: implement via ReportService."""
    raise NotImplementedError


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: uuid.UUID, db: Session = Depends(get_db)) -> ReportResponse:
    """Return a generated report. TODO: implement."""
    raise NotImplementedError
