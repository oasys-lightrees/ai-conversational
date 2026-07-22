"""End-to-end API tests for the report endpoints (guard paths; no model call).

The generate happy path calls the model, so it's covered in
test_report_service.py with a fake. Here we exercise the guard/not-found paths,
which reject before any model call.
"""

from __future__ import annotations

import uuid


def test_generate_unknown_assessment_returns_404(client):
    resp = client.post("/api/v1/report/generate", json={"assessment_id": str(uuid.uuid4())})
    assert resp.status_code == 404


def test_generate_incomplete_assessment_returns_409(client):
    started = client.post("/api/v1/assessment/start").json()
    resp = client.post(
        "/api/v1/report/generate",
        json={"assessment_id": started["assessment_id"]},
    )
    assert resp.status_code == 409


def test_get_unknown_report_returns_404(client):
    resp = client.get(f"/api/v1/report/{uuid.uuid4()}")
    assert resp.status_code == 404
