"""End-to-end API tests for /chat and /conversation.

The chat router constructs its own ChatService (and thus a real OpenAIService),
so these tests avoid triggering a model call: an empty message extracts nothing
and, with required fields still missing, the turn would call question-gen — so
we assert the not-found paths here and cover the model-driven flow in
test_chat_service.py with a faked model.
"""

from __future__ import annotations

import uuid


def test_chat_unknown_assessment_returns_404(client):
    resp = client.post(
        "/api/v1/chat",
        json={"assessment_id": str(uuid.uuid4()), "message": "halo"},
    )
    assert resp.status_code == 404


def test_conversation_unknown_assessment_returns_404(client):
    resp = client.get(f"/api/v1/conversation/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_conversation_empty_for_new_assessment(client):
    started = client.post("/api/v1/assessment/start").json()
    resp = client.get(f"/api/v1/conversation/{started['assessment_id']}")
    assert resp.status_code == 200
    assert resp.json() == []
