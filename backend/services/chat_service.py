"""Chat service — orchestrates a single assessment conversation turn.

Coordinates extraction, persistence, state tracking, and next-question
generation (Prompt 3). See ``docs/06-system-architecture.MD``.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.schemas.chat import ChatResponse, ConversationMessage
from backend.services.assessment_service import AssessmentService
from backend.services.extraction_service import ExtractionService
from backend.services.openai_service import OpenAIService
from backend.services.state_service import StateService


class ChatService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.openai = OpenAIService()
        self.assessments = AssessmentService(db)
        self.extraction = ExtractionService(self.openai)
        self.state = StateService(self.openai)

    def handle_message(self, assessment_id: uuid.UUID, message: str) -> ChatResponse:
        """Process one user turn and return the assistant reply.

        Flow (see docs): persist user message -> extract fields -> update
        assessment -> detect missing fields -> generate next question ->
        persist and return reply.

        TODO: implement the orchestration.
        """
        raise NotImplementedError

    def history(self, assessment_id: uuid.UUID) -> list[ConversationMessage]:
        """Return the ordered conversation history for an assessment.

        TODO: implement query.
        """
        raise NotImplementedError
