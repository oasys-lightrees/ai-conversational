"""Report service — Prompt 4 (Report Generator).

Generates the final business assessment report and structured recommendations.
See ``docs/05-prompt-design.MD``.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.models import Report
from backend.services.openai_service import OpenAIService


class ReportService:
    def __init__(self, db: Session, openai_service: OpenAIService | None = None) -> None:
        self.db = db
        self.openai = openai_service or OpenAIService()

    def generate(self, assessment_id: uuid.UUID) -> Report:
        """Generate and persist a report for a completed assessment.

        TODO: build the report prompt, parse output, persist Report +
        Recommendation rows.
        """
        raise NotImplementedError

    def get(self, report_id: uuid.UUID) -> Report | None:
        """Fetch a report by id.

        TODO: implement query.
        """
        raise NotImplementedError
