"""Tests for templates: seeding, resolution, and per-assessment config snapshot."""

from __future__ import annotations

import uuid

import pytest

from backend.models import Assessment
from backend.pipeline import DEFAULT_CONFIG
from backend.models import AssessmentTemplate
from backend.pipeline.seed import (
    SEEDS,
    refresh_builtin_templates,
    seed_default_templates,
)
from backend.services.template_service import TemplateNotFound, TemplateService


def test_seed_is_idempotent(db_session):
    seed_default_templates(db_session)
    seed_default_templates(db_session)
    templates = TemplateService(db_session).list()
    assert len(templates) == 2
    assert sum(1 for t in templates if t.is_default) == 1


def test_resolve_default(db_session):
    seed_default_templates(db_session)
    svc = TemplateService(db_session)
    template_id, config = svc.resolve_for_start(None)
    assert template_id is not None
    assert config.language == "id"


def test_resolve_unknown_raises(db_session):
    with pytest.raises(TemplateNotFound):
        TemplateService(db_session).resolve_for_start(uuid.uuid4())


def test_resolve_without_seed_falls_back_to_default_config(db_session):
    # No templates seeded -> built-in DEFAULT_CONFIG, no template id.
    template_id, config = TemplateService(db_session).resolve_for_start(None)
    assert template_id is None
    assert config.language == "id"


# --- API ---------------------------------------------------------------------


def test_list_and_get_templates(client, db_session):
    seed_default_templates(db_session)
    listing = client.get("/api/v1/templates")
    assert listing.status_code == 200
    body = listing.json()
    assert len(body) == 2
    assert any(t["is_default"] for t in body)

    one = body[0]
    detail = client.get(f"/api/v1/templates/{one['id']}")
    assert detail.status_code == 200
    assert "config" in detail.json()
    assert detail.json()["config"]["fields"]  # config carries the field specs


def test_get_unknown_template_404(client):
    resp = client.get(f"/api/v1/templates/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_start_with_template_snapshots_config(client, db_session):
    seed_default_templates(db_session)
    templates = client.get("/api/v1/templates").json()
    english = next(t for t in templates if t["language"] == "en")

    resp = client.post("/api/v1/assessment/start", json={"template_id": english["id"]})
    assert resp.status_code == 201
    assessment_id = resp.json()["assessment_id"]

    stored = db_session.get(Assessment, uuid.UUID(assessment_id))
    assert stored.template_id is not None
    assert stored.config_snapshot["language"] == "en"


def test_start_with_unknown_template_404(client):
    resp = client.post("/api/v1/assessment/start", json={"template_id": str(uuid.uuid4())})
    assert resp.status_code == 404


# --- refreshing the built-in templates --------------------------------------


def _always_required(config: dict) -> set[str]:
    return {f["name"] for f in config["fields"] if f["required"]}


def _seed_stale_default(db_session) -> None:
    """A database seeded before a DEFAULT_CONFIG change: same name, old config."""
    stale = SEEDS[0]["config"].model_copy(deep=True)
    for field in stale.fields:
        field.required = field.name == "property_type"
    db_session.add(
        AssessmentTemplate(
            name=SEEDS[0]["name"],
            description=SEEDS[0]["description"],
            is_default=True,
            config=stale.model_dump(),
        )
    )
    db_session.commit()


def test_seeding_alone_does_not_update_an_existing_template(db_session):
    _seed_stale_default(db_session)
    seed_default_templates(db_session)
    _id, config = TemplateService(db_session).resolve_for_start(None)
    assert {f.name for f in config.fields if f.required} == {"property_type"}


def test_refresh_pulls_default_config_through(db_session):
    _seed_stale_default(db_session)
    seed_default_templates(db_session)

    assert refresh_builtin_templates(db_session) == [SEEDS[0]["name"]]

    _id, config = TemplateService(db_session).resolve_for_start(None)
    expected = {f.name for f in DEFAULT_CONFIG.fields if f.required}
    assert {f.name for f in config.fields if f.required} == expected


def test_refresh_is_idempotent_and_keeps_identity(db_session):
    seed_default_templates(db_session)
    assert refresh_builtin_templates(db_session) == []

    template = TemplateService(db_session).default()
    assert template.name == SEEDS[0]["name"]
    assert template.is_default is True


def test_refresh_leaves_operator_templates_alone(db_session):
    seed_default_templates(db_session)
    custom = SEEDS[0]["config"].model_copy(deep=True)
    for field in custom.fields:
        field.required = False
    custom.fields[0].required = True
    mine = TemplateService(db_session).create("Mine", None, False, custom)
    before = _always_required(mine.config)

    refresh_builtin_templates(db_session)

    db_session.refresh(mine)
    assert _always_required(mine.config) == before


def test_refresh_does_not_disturb_in_flight_assessments(client, db_session):
    _seed_stale_default(db_session)
    seed_default_templates(db_session)
    started = client.post("/api/v1/assessment/start", json={})
    assessment_id = uuid.UUID(started.json()["assessment_id"])

    refresh_builtin_templates(db_session)

    stored = db_session.get(Assessment, assessment_id)
    snapshot = TemplateService(db_session).config_for(stored)
    # The run keeps the scope it started with.
    assert {f.name for f in snapshot.fields if f.required} == {"property_type"}
