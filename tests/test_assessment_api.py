"""End-to-end API tests for the assessment endpoints (Phase 1b exit criteria).

Exercises POST /assessment/start, GET /assessment/{id}, and DELETE through the
real FastAPI app against Postgres, with no OpenAI key set.
"""

from __future__ import annotations

import uuid


def test_assessment_lifecycle(client):
    # start
    resp = client.post("/api/v1/assessment/start")
    assert resp.status_code == 201
    body = resp.json()
    assessment_id = body["assessment_id"]
    assert body["status"] == "IN_PROGRESS"

    # get
    resp = client.get(f"/api/v1/assessment/{assessment_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["completion_percentage"] == 0
    assert body["assessment_data"] == {}

    # delete
    resp = client.delete(f"/api/v1/assessment/{assessment_id}")
    assert resp.status_code == 204

    # gone
    resp = client.get(f"/api/v1/assessment/{assessment_id}")
    assert resp.status_code == 404


def test_get_unknown_returns_404(client):
    resp = client.get(f"/api/v1/assessment/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_delete_unknown_returns_404(client):
    resp = client.delete(f"/api/v1/assessment/{uuid.uuid4()}")
    assert resp.status_code == 404
