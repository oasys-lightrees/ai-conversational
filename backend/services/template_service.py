"""Template service — resolve and load pipeline configs from stored templates."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import AssessmentTemplate
from backend.pipeline import DEFAULT_CONFIG, PipelineConfig


class TemplateNotFound(Exception):
    """Raised when a template id does not exist."""


class TemplateService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[AssessmentTemplate]:
        return list(
            self.db.scalars(select(AssessmentTemplate).order_by(AssessmentTemplate.name)).all()
        )

    def get(self, template_id: uuid.UUID) -> AssessmentTemplate | None:
        return self.db.get(AssessmentTemplate, template_id)

    def default(self) -> AssessmentTemplate | None:
        return self.db.scalar(
            select(AssessmentTemplate).where(AssessmentTemplate.is_default.is_(True))
        )

    def resolve_for_start(
        self, template_id: uuid.UUID | None = None
    ) -> tuple[uuid.UUID | None, PipelineConfig]:
        """Return ``(template_id, config)`` to snapshot onto a new assessment.

        Explicit id → that template (or :class:`TemplateNotFound`); otherwise the
        default template; otherwise the built-in ``DEFAULT_CONFIG``.
        """
        if template_id is not None:
            template = self.get(template_id)
            if template is None:
                raise TemplateNotFound(str(template_id))
            return template.id, PipelineConfig(**template.config)
        template = self.default()
        if template is not None:
            return template.id, PipelineConfig(**template.config)
        return None, DEFAULT_CONFIG

    def config_for(self, assessment) -> PipelineConfig:
        """Load the config an existing assessment was started with."""
        if assessment.config_snapshot:
            return PipelineConfig(**assessment.config_snapshot)
        return DEFAULT_CONFIG
