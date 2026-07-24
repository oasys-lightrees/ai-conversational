"""Seed the built-in assessment templates.

Idempotent: templates are upserted by name. Called from ``init_db`` and safe to
re-run. (Template CRUD via API is deferred; these are the seeded starting set.)
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
