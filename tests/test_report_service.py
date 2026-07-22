"""Tests for ReportService (DB-backed; model faked)."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import func, select

from backend.models import Report
from backend.models.enums import AssessmentStatus, RecommendationPriority
from backend.services.assessment_service import AssessmentNotFound, AssessmentService
from backend.services.report_service import AssessmentNotCompleted, ReportService
from tests.conftest import FakeOpenAIService

_REPORT_JSON = {
    "executive_summary": "Ringkasan eksekutif",
    "business_analysis": "Analisis bisnis",
    "operational_analysis": "Analisis operasional",
    "technology_analysis": "Analisis teknologi",
    "ai_readiness": "Kesiapan AI",
    "recommendations_summary": "Ringkasan rekomendasi",
    "next_steps": "Langkah berikutnya",
    "recommendations": [
        {"title": "AI Receptionist", "description": "d1", "priority": "HIGH", "estimated_impact": "tinggi"},
        {"title": "Dynamic Pricing", "description": "d2", "priority": "medium", "estimated_impact": "sedang"},
    ],
}


def _completed_assessment(db):
    svc = AssessmentService(db)
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
    db.commit()
    return assessment


def test_generate_persists_report_and_recommendations(db_session):
    assessment = _completed_assessment(db_session)
    fake = FakeOpenAIService(json_result=_REPORT_JSON)
    report = ReportService(db_session, openai_service=fake).generate(assessment.id)

    assert report.executive_summary == "Ringkasan eksekutif"
    assert report.next_steps == "Langkah berikutnya"
    assert len(report.recommendations) == 2
    priorities = {r.title: r.priority for r in report.recommendations}
    assert priorities["AI Receptionist"] == RecommendationPriority.HIGH
    assert priorities["Dynamic Pricing"] == RecommendationPriority.MEDIUM  # coerced from "medium"


def test_generate_rejects_incomplete_assessment(db_session):
    svc = AssessmentService(db_session)
    assessment = svc.create()  # IN_PROGRESS
    with pytest.raises(AssessmentNotCompleted):
        ReportService(db_session, openai_service=FakeOpenAIService(json_result=_REPORT_JSON)).generate(
            assessment.id
        )


def test_generate_unknown_assessment(db_session):
    with pytest.raises(AssessmentNotFound):
        ReportService(db_session, openai_service=FakeOpenAIService()).generate(uuid.uuid4())


def test_generate_is_idempotent(db_session):
    assessment = _completed_assessment(db_session)
    svc = ReportService(db_session, openai_service=FakeOpenAIService(json_result=_REPORT_JSON))
    first = svc.generate(assessment.id)
    second = svc.generate(assessment.id)

    assert first.id != second.id
    count = db_session.scalar(
        select(func.count()).select_from(Report).where(Report.assessment_id == assessment.id)
    )
    assert count == 1  # old report replaced, not duplicated


def test_generate_skips_recommendation_without_title(db_session):
    assessment = _completed_assessment(db_session)
    payload = dict(_REPORT_JSON)
    payload["recommendations"] = [
        {"description": "no title here", "priority": "HIGH"},
        {"title": "Valid", "priority": "LOW"},
    ]
    report = ReportService(db_session, openai_service=FakeOpenAIService(json_result=payload)).generate(
        assessment.id
    )
    assert [r.title for r in report.recommendations] == ["Valid"]


def test_get_returns_report_or_none(db_session):
    assessment = _completed_assessment(db_session)
    svc = ReportService(db_session, openai_service=FakeOpenAIService(json_result=_REPORT_JSON))
    report = svc.generate(assessment.id)
    assert svc.get(report.id).id == report.id
    assert svc.get(uuid.uuid4()) is None
