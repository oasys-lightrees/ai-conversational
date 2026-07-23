"""End-to-end API tests for the report endpoints (guard paths; no model call).

The generate happy path calls the model, so it's covered in
test_report_service.py with a fake. Here we exercise the guard/not-found paths,
which reject before any model call.
"""

from __future__ import annotations

import uuid

from backend.models.enums import AssessmentStatus
from backend.services.assessment_service import AssessmentService
from backend.services.report_service import ReportService
from tests.conftest import FakeOpenAIService


def test_get_report_includes_assessment_id(client, db_session):
    # Build a completed assessment + report on the same session the client uses.
    svc = AssessmentService(db_session)
    assessment = svc.create()
    svc.update_data(
        assessment.id,
        {
            "property_type": "Villa",
            "location": "Bali",
            "business_stage": "Underperforming",
            "occupancy_rate": 55,
            "monthly_revenue": 1000,
            "average_room_rate": 100,
            "booking_channels": ["Airbnb"],
        },
    )
    assessment = svc.get(assessment.id)
    assessment.status = AssessmentStatus.COMPLETED
    db_session.commit()

    report = ReportService(
        db_session, openai_service=FakeOpenAIService(json_result={"executive_summary": "x"})
    ).generate(assessment.id)

    resp = client.get(f"/api/v1/report/{report.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["report_id"] == str(report.id)
    # The report page needs this to fetch the assessment's property summary.
    assert body["assessment_id"] == str(assessment.id)


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
