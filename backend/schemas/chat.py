"""Request/response schemas for the chat endpoint."""

from __future__ import annotations

import uuid

from pydantic import BaseModel

from backend.models.enums import ConversationRole


class ChatRequest(BaseModel):
    assessment_id: uuid.UUID
    message: str


class ChatResponse(BaseModel):
    reply: str
    completion_percentage: int
    next_stage: str | None = None


class ConversationMessage(BaseModel):
    role: ConversationRole
    message: str
