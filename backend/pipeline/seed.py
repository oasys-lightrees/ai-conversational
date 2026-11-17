"""Seed the built-in assessment templates.

Idempotent: a template whose name already exists is left untouched, so re-running
never clobbers operator edits. Called from ``init_db`` and safe to re-run.

Because of that, a change to ``DEFAULT_CONFIG`` does **not** reach a database
that has already been seeded — new assessments resolve their config from the
stored template, not from ``DEFAULT_CONFIG``. Use
:func:`refresh_builtin_templates` to pull such a change through.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import AssessmentTemplate
from backend.pipeline.default_config import DEFAULT_CONFIG

SEEDS = [
    {
        "name": "Default (Hospitality, ID)",
        "description": "Hospitality property assessment in Bahasa Indonesia.",
        "is_default": True,
        "config": DEFAULT_CONFIG,
    },
    {
        "name": "Hospitality (EN)",
        "description": "Hospitality property assessment in English.",
        "is_default": False,
        "config": DEFAULT_CONFIG.model_copy(update={"language": "en"}),
    },
]


def seed_default_templates(session: Session) -> None:
    existing = {t.name for t in session.scalars(select(AssessmentTemplate)).all()}
    for seed in SEEDS:
        if seed["name"] in existing:
            continue
        session.add(
            AssessmentTemplate(
                name=seed["name"],
                description=seed["description"],
                is_default=seed["is_default"],
                config=seed["config"].model_dump(),
            )
        )
    session.commit()


def refresh_builtin_templates(session: Session) -> list[str]:
    """Re-sync the built-in templates' configs to the current ``DEFAULT_CONFIG``.

    The opt-in counterpart to :func:`seed_default_templates`, which only ever
    inserts. Run it after changing ``DEFAULT_CONFIG``::

        python -m backend.database.init_db --refresh-builtins

    Touches only the templates in :data:`SEEDS` (matched by name) and only their
    ``config`` — operator-created templates are left alone. Hand-edits made to a
    built-in template through the admin UI *are* overwritten, which is why this
    is deliberately not part of the normal bootstrap.

    In-flight assessments are unaffected: each one runs against the config
    snapshotted onto it at start. Returns the names it changed.
    """
    by_name = {t.name: t for t in session.scalars(select(AssessmentTemplate)).all()}
    updated: list[str] = []
    for seed in SEEDS:
        template = by_name.get(seed["name"])
        if template is None:
            continue
        config = seed["config"].model_dump()
        if template.config != config:
            template.config = config
            updated.append(template.name)
    session.commit()
    return updated
