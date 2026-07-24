"""Admin API tests: auth gating, template CRUD/validation, assessments, metrics."""

from __future__ import annotations

import uuid

from backend.models.enums import AssessmentStatus
from backend.pipeline.seed import seed_default_templates
from backend.services.assessment_service import AssessmentService


def _template_body(name="Custom", is_default=False):
    return {
        "name": name,
        "description": "A custom template.",
        "is_default": is_default,
        "config": {
            "knowledge": "K",
            "style": "S",
            "language": "en",
            "fields": [
                {"name": "property_type", "type": "enum", "enum_options": ["VILLA"], "required": True},
                {"name": "wifi_speed", "type": "integer", "required": True},
            ],
        },
    }


# --- Auth gating -------------------------------------------------------------


def test_admin_requires_auth(client, admin_headers):
    # No/incorrect token -> 401 (key is configured via the fixture).
    assert client.get("/api/v1/admin/templates").status_code == 401
    assert client.get(
        "/api/v1/admin/templates", headers={"Authorization": "Bearer wrong"}
    ).status_code == 401
    assert client.get("/api/v1/admin/templates", headers=admin_headers).status_code == 200


def test_admin_disabled_when_unconfigured(client):
    # No admin_headers fixture -> key empty -> 503.
    assert client.get("/api/v1/admin/metrics").status_code == 503


# --- Template CRUD -----------------------------------------------------------


def test_create_get_update_delete_template(client, admin_headers):
    created = client.post("/api/v1/admin/templates", json=_template_body(), headers=admin_headers)
    assert created.status_code == 201
    template_id = created.json()["id"]

    got = client.get(f"/api/v1/admin/templates/{template_id}", headers=admin_headers)
    assert got.status_code == 200
    assert got.json()["config"]["language"] == "en"

    body = _template_body(name="Renamed")
    updated = client.put(f"/api/v1/admin/templates/{template_id}", json=body, headers=admin_headers)
    assert updated.status_code == 200
    assert updated.json()["name"] == "Renamed"

    assert client.delete(f"/api/v1/admin/templates/{template_id}", headers=admin_headers).status_code == 204
    assert client.get(f"/api/v1/admin/templates/{template_id}", headers=admin_headers).status_code == 404


def test_create_invalid_config_422(client, admin_headers):
    body = _template_body()
    body["config"]["fields"] = [{"name": "x", "type": "enum", "enum_options": []}]  # enum without options
    resp = client.post("/api/v1/admin/templates", json=body, headers=admin_headers)
    assert resp.status_code == 422


def test_duplicate_name_409(client, admin_headers):
    client.post("/api/v1/admin/templates", json=_template_body(name="Dup"), headers=admin_headers)
    resp = client.post("/api/v1/admin/templates", json=_template_body(name="Dup"), headers=admin_headers)
    assert resp.status_code == 409


def test_clone_and_set_default(client, admin_headers):
    created = client.post("/api/v1/admin/templates", json=_template_body(name="Base"), headers=admin_headers)
    tid = created.json()["id"]

    cloned = client.post(f"/api/v1/admin/templates/{tid}/clone", headers=admin_headers)
    assert cloned.status_code == 201
    assert cloned.json()["name"] == "Base (copy)"

    defaulted = client.post(f"/api/v1/admin/templates/{tid}/default", headers=admin_headers)
    assert defaulted.status_code == 200
    assert defaulted.json()["is_default"] is True


def test_delete_in_use_template_409(client, db_session, admin_headers):
    seed_default_templates(db_session)
    templates = client.get("/api/v1/admin/templates", headers=admin_headers).json()
    default = next(t for t in templates if t["is_default"])
    # Start an assessment referencing it.
    client.post("/api/v1/assessment/start", json={"template_id": default["id"]})
    resp = client.delete(f"/api/v1/admin/templates/{default['id']}", headers=admin_headers)
    assert resp.status_code == 409


# --- Assessments browser -----------------------------------------------------


def test_assessments_list_and_detail(client, db_session, admin_headers):
    svc = AssessmentService(db_session)
    a = svc.create()
    svc.update_data(a.id, {"property_type": "Villa", "location": "Bali"})

    listing = client.get("/api/v1/admin/assessments", headers=admin_headers)
    assert listing.status_code == 200
    body = listing.json()
    assert body["total"] == 1
    assert body["items"][0]["assessment_id"] == str(a.id)

    detail = client.get(f"/api/v1/admin/assessments/{a.id}", headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["assessment_data"]["property_location"] == "Bali"


def test_assessments_status_filter(client, db_session, admin_headers):
    svc = AssessmentService(db_session)
    svc.create()  # IN_PROGRESS
    completed = svc.create()
    completed.status = AssessmentStatus.COMPLETED
    db_session.commit()

    resp = client.get("/api/v1/admin/assessments?status=COMPLETED", headers=admin_headers)
    assert resp.json()["total"] == 1


def test_admin_delete_assessment(client, db_session, admin_headers):
    a = AssessmentService(db_session).create()
    assert client.delete(f"/api/v1/admin/assessments/{a.id}", headers=admin_headers).status_code == 204
    assert client.get(f"/api/v1/admin/assessments/{a.id}", headers=admin_headers).status_code == 404


# --- Metrics -----------------------------------------------------------------


def test_metrics(client, db_session, admin_headers):
    svc = AssessmentService(db_session)
    svc.create()
    done = svc.create()
    done.status = AssessmentStatus.COMPLETED
    db_session.commit()
    svc.update_data(done.id, {"property_type": "Villa"})

    resp = client.get("/api/v1/admin/metrics", headers=admin_headers)
    assert resp.status_code == 200
    m = resp.json()
    assert m["total_assessments"] == 2
    assert m["by_status"]["COMPLETED"] == 1
    assert m["completion_rate"] == 0.5
    assert any(n["key"] == "VILLA" for n in m["by_property_type"])
