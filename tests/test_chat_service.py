"""Tests for ChatService turn orchestration (DB-backed; model faked)."""

from __future__ import annotations

import uuid

import pytest

from backend.models.enums import AssessmentStatus, ConversationRole, PropertyType
from backend.services.assessment_service import AssessmentNotFound, AssessmentService
from backend.services.chat_service import (
    CLOSING_MESSAGE,
    FALLBACK_GENERIC,
    FALLBACK_REPHRASE,
    ChatService,
)
from backend.services.openai_service import OpenAIServiceError
from tests.conftest import FakeOpenAIService


def _new_assessment(db):
    return AssessmentService(db).create()


def test_turn_extracts_persists_and_asks_next_question(db_session):
    fake = FakeOpenAIService(
        json_result={"property_type": "Villa", "location": "Bali"},
        text_result="Apa tahap bisnis properti Anda saat ini?",
    )
    assessment = _new_assessment(db_session)
    svc = ChatService(db_session, openai_service=fake)

    resp = svc.handle_message(assessment.id, "Saya punya villa di Bali")

    assert resp.reply == "Apa tahap bisnis properti Anda saat ini?"
    # property_type + location present, business_stage missing -> 2/3
    assert resp.completion_percentage == 67
    assert resp.next_stage == "BUSINESS_STAGE"

    refreshed = AssessmentService(db_session).get(assessment.id)
    assert refreshed.data.property_type == PropertyType.VILLA
    assert refreshed.data.property_location == "Bali"

    history = svc.history(assessment.id)
    assert [m.role for m in history] == [ConversationRole.USER, ConversationRole.ASSISTANT]
    assert history[0].message == "Saya punya villa di Bali"


def test_turn_completes_when_all_required_present(db_session):
    fake = FakeOpenAIService(
        json_result={
            "property_type": "Villa",
            "location": "Bali",
            "business_stage": "Underperforming",
            "occupancy_rate": 55,
            "monthly_revenue": 1000,
            "average_room_rate": 100,
            "booking_channels": ["Airbnb"],
        },
        text_result="(should not be used)",
    )
    assessment = _new_assessment(db_session)
    svc = ChatService(db_session, openai_service=fake)

    resp = svc.handle_message(assessment.id, "info lengkap")

    assert resp.reply == CLOSING_MESSAGE
    assert resp.completion_percentage == 100
    assert resp.next_stage == "COMPLETE"

    refreshed = AssessmentService(db_session).get(assessment.id)
    assert refreshed.status == AssessmentStatus.COMPLETED
    assert refreshed.completed_at is not None


def test_extraction_failure_asks_to_rephrase_without_updating(db_session):
    fake = FakeOpenAIService(json_exc=OpenAIServiceError("boom"))
    assessment = _new_assessment(db_session)
    svc = ChatService(db_session, openai_service=fake)

    resp = svc.handle_message(assessment.id, "pesan tidak jelas")

    assert resp.reply == FALLBACK_REPHRASE
    assert resp.completion_percentage == 0
    refreshed = AssessmentService(db_session).get(assessment.id)
    assert refreshed.data.property_type is None
    # user + assistant still recorded
    assert len(svc.history(assessment.id)) == 2


def test_question_failure_keeps_extracted_data(db_session):
    fake = FakeOpenAIService(
        json_result={"property_type": "Villa", "location": "Bali"},
        text_exc=OpenAIServiceError("boom"),
    )
    assessment = _new_assessment(db_session)
    svc = ChatService(db_session, openai_service=fake)

    resp = svc.handle_message(assessment.id, "Saya punya villa di Bali")

    assert resp.reply == FALLBACK_GENERIC
    refreshed = AssessmentService(db_session).get(assessment.id)
    assert refreshed.data.property_type == PropertyType.VILLA  # data survived


def test_unknown_assessment_raises(db_session):
    svc = ChatService(db_session, openai_service=FakeOpenAIService())
    with pytest.raises(AssessmentNotFound):
        svc.handle_message(uuid.uuid4(), "hi")


def test_history_ordered_across_turns(db_session):
    fake = FakeOpenAIService(json_result={}, text_result="Pertanyaan?")
    assessment = _new_assessment(db_session)
    svc = ChatService(db_session, openai_service=fake)

    svc.handle_message(assessment.id, "pesan satu")
    svc.handle_message(assessment.id, "pesan dua")

    messages = [m.message for m in svc.history(assessment.id)]
    assert messages == ["pesan satu", "Pertanyaan?", "pesan dua", "Pertanyaan?"]
