"""Template service — resolve and load pipeline configs from stored templates."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from backend.models import Assessment, AssessmentTemplate
from backend.pipeline import DEFAULT_CONFIG, PipelineConfig


class TemplateNotFound(Exception):
    """Raised when a template id does not exist."""


class TemplateInvalid(Exception):
    """Raised when a template's config fails validation."""


class DuplicateTemplateName(Exception):
    """Raised when a template name already exists."""


class TemplateInUse(Exception):
    """Raised when deleting a template still referenced by assessments."""


def validate_config(config: PipelineConfig) -> None:
    """Validate a pipeline config; raise :class:`TemplateInvalid` on any problem."""
    names = [field.name for field in config.fields]
    if not names:
        raise TemplateInvalid("config must define at least one field")
    if len(names) != len(set(names)):
        raise TemplateInvalid("duplicate field names")
    known = set(names)
    for field in config.fields:
        if field.type == "enum" and not field.enum_options:
            raise TemplateInvalid(f"enum field '{field.name}' needs enum_options")
        if field.required_when:
            for referenced in field.required_when:
                if referenced not in known:
                    raise TemplateInvalid(
                        f"required_when on '{field.name}' references unknown field '{referenced}'"
                    )


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

    # -- admin CRUD ------------------------------------------------------------

    def create(
        self, name: str, description: str | None, is_default: bool, config: PipelineConfig
    ) -> AssessmentTemplate:
        validate_config(config)
        if self.db.scalar(select(AssessmentTemplate).where(AssessmentTemplate.name == name)):
            raise DuplicateTemplateName(name)
        if is_default:
            self._clear_defaults()
        template = AssessmentTemplate(
            name=name, description=description, is_default=is_default, config=config.model_dump()
        )
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def update(
        self,
        template_id: uuid.UUID,
        name: str,
        description: str | None,
        is_default: bool,
        config: PipelineConfig,
    ) -> AssessmentTemplate:
        template = self.get(template_id)
        if template is None:
            raise TemplateNotFound(str(template_id))
        validate_config(config)
        clash = self.db.scalar(
            select(AssessmentTemplate).where(
                AssessmentTemplate.name == name, AssessmentTemplate.id != template_id
            )
        )
        if clash:
            raise DuplicateTemplateName(name)
        if is_default and not template.is_default:
            self._clear_defaults()
        template.name = name
        template.description = description
        template.is_default = is_default
        template.config = config.model_dump()
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete(self, template_id: uuid.UUID) -> None:
        template = self.get(template_id)
        if template is None:
            raise TemplateNotFound(str(template_id))
        referenced = self.db.scalar(
            select(func.count()).select_from(Assessment).where(
                Assessment.template_id == template_id
            )
        )
        if referenced:
            raise TemplateInUse(str(template_id))
        self.db.delete(template)
        self.db.commit()

    def clone(self, template_id: uuid.UUID) -> AssessmentTemplate:
        template = self.get(template_id)
        if template is None:
            raise TemplateNotFound(str(template_id))
        name = f"{template.name} (copy)"
        suffix = 2
        while self.db.scalar(select(AssessmentTemplate).where(AssessmentTemplate.name == name)):
            name = f"{template.name} (copy {suffix})"
            suffix += 1
        clone = AssessmentTemplate(
            name=name, description=template.description, is_default=False, config=template.config
        )
        self.db.add(clone)
        self.db.commit()
        self.db.refresh(clone)
        return clone

    def set_default(self, template_id: uuid.UUID) -> AssessmentTemplate:
        template = self.get(template_id)
        if template is None:
            raise TemplateNotFound(str(template_id))
        self._clear_defaults()
        template.is_default = True
        self.db.commit()
        self.db.refresh(template)
        return template

    def _clear_defaults(self) -> None:
        self.db.execute(update(AssessmentTemplate).values(is_default=False))
