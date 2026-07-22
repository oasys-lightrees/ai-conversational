"""Report service — Prompt 4 (Report Generator).

Generates the final business assessment report and structured recommendations
for a *completed* assessment (``docs/05``). The model is prompted to return JSON
keyed by the actual ``Report`` columns (the G3 resolution: DB vocabulary is
canonical), plus a list of recommendations. Regeneration is idempotent — any
existing report for the assessment is replaced.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Recommendation, Report
from backend.models.enums import AssessmentStatus, RecommendationPriority
from backend.services.assessment_service import AssessmentNotFound, AssessmentService
from backend.services.openai_service import OpenAIService

# Report columns the model is asked to fill (all free-text sections).
_REPORT_SECTIONS = (
    "executive_summary",
    "business_analysis",
    "operational_analysis",
    "technology_analysis",
    "ai_readiness",
    "recommendations_summary",
    "next_steps",
)

_SYSTEM_PROMPT = """\
You are a hospitality business analyst. Given an assessment of a property, write \
a concise AI-readiness assessment report in Bahasa Indonesia.

Return ONLY a JSON object with these string fields: executive_summary, \
business_analysis, operational_analysis, technology_analysis, ai_readiness, \
recommendations_summary, next_steps. Also include "recommendations": a list of \
objects with fields title, description, priority (one of LOW, MEDIUM, HIGH), and \
estimated_impact. Base everything strictly on the provided data; do not invent \
facts.
"""


class AssessmentNotCompleted(Exception):
    """Raised when a report is requested for an assessment that is not COMPLETED."""


class ReportService:
    def __init__(self, db: Session, openai_service: OpenAIService | None = None) -> None:
        self.db = db
        self.openai = openai_service or OpenAIService()
        self.assessments = AssessmentService(db)

    def generate(self, assessment_id: uuid.UUID) -> Report:
        """Generate and persist a report for a completed assessment.

        Raises :class:`AssessmentNotFound` if the id is unknown, or
        :class:`AssessmentNotCompleted` if the assessment is not COMPLETED.
        """
        assessment = self.assessments.get(assessment_id)
        if assessment is None:
            raise AssessmentNotFound(str(assessment_id))
        if assessment.status != AssessmentStatus.COMPLETED:
            raise AssessmentNotCompleted(str(assessment_id))

        state = self.assessments.to_state_dict(assessment.data)
        raw = self.openai.complete_json(_SYSTEM_PROMPT, f"Assessment data: {state}")

        # Idempotent: replace any existing report for this assessment.
        existing = self.db.scalar(
            select(Report).where(Report.assessment_id == assessment_id)
        )
        if existing is not None:
            self.db.delete(existing)
            self.db.flush()

        report = Report(
            assessment_id=assessment_id,
            **{section: _as_text(raw.get(section)) for section in _REPORT_SECTIONS},
        )
        report.recommendations = self._parse_recommendations(raw.get("recommendations"))

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get(self, report_id: uuid.UUID) -> Report | None:
        """Fetch a report by id, or ``None`` if it does not exist."""
        return self.db.get(Report, report_id)

    def _parse_recommendations(self, raw_items) -> list[Recommendation]:
        if not isinstance(raw_items, list):
            return []
        recommendations: list[Recommendation] = []
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            title = _as_text(item.get("title"))
            if not title:  # title is NOT NULL — skip malformed entries
                continue
            recommendations.append(
                Recommendation(
                    title=title,
                    description=_as_text(item.get("description")),
                    priority=_coerce_priority(item.get("priority")),
                    estimated_impact=_as_text(item.get("estimated_impact")),
                )
            )
        return recommendations


def _as_text(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _coerce_priority(value) -> RecommendationPriority:
    if isinstance(value, RecommendationPriority):
        return value
    key = str(value).strip().upper()
    return RecommendationPriority.__members__.get(key, RecommendationPriority.MEDIUM)
