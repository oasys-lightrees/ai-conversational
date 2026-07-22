"""Assessment service — persistence of assessment data.

Responsible for creating assessments, updating collected data, and validating
required fields. See ``docs/06-system-architecture.MD``.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.models import Assessment


class AssessmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self) -> Assessment:
        """Create a new assessment session with empty data.

        TODO: create Assessment + AssessmentData rows and persist.
        """
        raise NotImplementedError

    def get(self, assessment_id: uuid.UUID) -> Assessment | None:
        """Fetch an assessment by id.

        TODO: implement query.
        """
        raise NotImplementedError

    def update_data(self, assessment_id: uuid.UUID, fields: dict) -> Assessment:
        """Merge extracted ``fields`` into the assessment data.

        TODO: implement update + progress recalculation.
        """
        raise NotImplementedError

    def delete(self, assessment_id: uuid.UUID) -> None:
        """Delete or archive an assessment.

        TODO: implement deletion.
        """
        raise NotImplementedError
