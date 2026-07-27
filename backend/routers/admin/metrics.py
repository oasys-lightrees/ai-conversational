"""Admin metrics — aggregate stats computed from the current schema."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Assessment, AssessmentData
from backend.models.enums import AssessmentStatus
from backend.schemas.admin import Metrics, NamedCount

router = APIRouter(tags=["admin:metrics"])


def _grouped_counts(db: Session, column) -> list[NamedCount]:
    rows = db.execute(
        select(column, func.count()).where(column.isnot(None)).group_by(column)
    ).all()
    result = []
    for key, count in rows:
        # Enum columns come back as members; use their value.
        label = key.value if hasattr(key, "value") else str(key)
        result.append(NamedCount(key=label, count=count))
    return sorted(result, key=lambda n: n.count, reverse=True)


@router.get("/metrics", response_model=Metrics)
def get_metrics(db: Session = Depends(get_db)) -> Metrics:
    total = db.scalar(select(func.count()).select_from(Assessment)) or 0

    by_status: dict[str, int] = {status.value: 0 for status in AssessmentStatus}
    for status_value, count in db.execute(
        select(Assessment.status, func.count()).group_by(Assessment.status)
    ).all():
        by_status[status_value.value] = count

    completed = by_status.get(AssessmentStatus.COMPLETED.value, 0)
    average_completion = db.scalar(select(func.avg(Assessment.completion_percentage))) or 0

    return Metrics(
        total_assessments=total,
        by_status=by_status,
        completion_rate=round(completed / total, 4) if total else 0.0,
        average_completion=round(float(average_completion), 2),
        by_property_type=_grouped_counts(db, AssessmentData.property_type),
        by_business_stage=_grouped_counts(db, AssessmentData.business_stage),
    )
