"""Assessment service — persistence of assessment data.

Creates assessments, merges extracted fields onto the ``AssessmentData`` row,
recomputes completion, and deletes. Contains **no AI calls**, so it works with
no ``OPENAI_API_KEY`` set. Field translation is delegated to
``field_mapping``; completion is recomputed via ``StateService`` so that
``update_data`` is the single writer of ``completion_percentage`` (Decision D3).
See ``docs/10-implementation-plan.MD``.
"""

from __future__ import annotations

import enum
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from backend.models import Assessment, AssessmentData
from backend.pipeline import DEFAULT_CONFIG, FieldMapper, PipelineConfig
from backend.services.state_service import StateService

# Columns excluded from the flat state dict (system/bookkeeping, not content).
_STATE_EXCLUDE = {"id", "assessment_id", "created_at", "updated_at"}


class AssessmentNotFound(Exception):
    """Raised when an assessment id does not exist."""


class AssessmentService:
    def __init__(
        self,
        db: Session,
        state_service: StateService | None = None,
        config: PipelineConfig | None = None,
    ) -> None:
        self.db = db
        self.config = config or DEFAULT_CONFIG
        self.state = state_service or StateService(config=self.config)
        self.mapper = FieldMapper(self.config)

    def create(self) -> Assessment:
        """Create a new assessment session with an empty data row."""
        assessment = Assessment()
        assessment.data = AssessmentData()
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def get(self, assessment_id: uuid.UUID) -> Assessment | None:
        """Fetch an assessment by id, or ``None`` if it does not exist."""
        return self.db.get(Assessment, assessment_id)

    def update_data(self, assessment_id: uuid.UUID, fields: dict) -> Assessment:
        """Merge extracted ``fields`` onto the assessment and recompute progress.

        Raises :class:`AssessmentNotFound` if the id is unknown.
        """
        assessment = self.get(assessment_id)
        if assessment is None:
            raise AssessmentNotFound(str(assessment_id))

        data = assessment.data
        if data is None:  # defensive: rows created without a data row
            data = AssessmentData(assessment_id=assessment.id)
            assessment.data = data

        columns, extra = self.mapper.map(fields)
        for key, value in columns.items():
            setattr(data, key, value)
        if extra:
            merged = dict(data.branch_data or {})
            merged.update(extra)
            data.branch_data = merged

        # Sole writer of completion_percentage (Decision D3).
        assessment.completion_percentage = self.state.completion_percentage(
            self.to_state_dict(data)
        )

        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def delete(self, assessment_id: uuid.UUID) -> None:
        """Hard-delete an assessment (cascades to data/conversations/report).

        Raises :class:`AssessmentNotFound` if the id is unknown.
        """
        assessment = self.get(assessment_id)
        if assessment is None:
            raise AssessmentNotFound(str(assessment_id))
        self.db.delete(assessment)
        self.db.commit()

    def to_state_dict(self, data: AssessmentData | None) -> dict[str, Any]:
        """Flatten an ``AssessmentData`` row into the dict StateService expects.

        Non-null column values only (enums as their ``.value`` string); the
        ``branch_data`` blob is flattened to the top level.
        """
        state: dict[str, Any] = {}
        if data is None:
            return state
        for column in data.__table__.columns:
            name = column.name
            if name in _STATE_EXCLUDE:
                continue
            value = getattr(data, name)
            if value is None:
                continue
            if name == "branch_data":
                if isinstance(value, dict):
                    state.update(value)
                continue
            if isinstance(value, enum.Enum):
                value = value.value
            elif isinstance(value, Decimal):
                # Serialize numeric columns as JSON numbers, not strings, so the
                # API contract is consistent with integer columns.
                value = float(value)
            state[name] = value
        return state
