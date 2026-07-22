"""Chat service — orchestrates a single assessment conversation turn.

Coordinates extraction, persistence, state tracking, and next-question
generation (Prompt 3). See ``docs/05`` and ``docs/10``.

Partial-failure policy (a turn makes up to two model calls — extraction, then
question generation). Both are caught individually so a turn never loses
progress:

- Extraction fails  -> persist the user message, skip the data update, ask the
  user to rephrase.
- Extraction succeeds but question generation fails -> the extracted data is
  already committed; return a graceful generic reply.

Both rely on the single ``OpenAIServiceError`` from ``OpenAIService``.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Conversation
from backend.models.enums import AssessmentStatus, ConversationRole
from backend.schemas.chat import ChatResponse, ConversationMessage
from backend.services.assessment_service import AssessmentNotFound, AssessmentService
from backend.services.extraction_service import ExtractionService
from backend.services.openai_service import OpenAIService, OpenAIServiceError
from backend.services.state_service import StateService

# User-facing copy is Bahasa Indonesia (docs/05).
CLOSING_MESSAGE = (
    "Terima kasih! Semua informasi yang dibutuhkan sudah terkumpul. "
    "Kami akan menyiapkan laporan asesmen Anda."
)
FALLBACK_REPHRASE = (
    "Maaf, saya belum sepenuhnya menangkap informasinya. "
    "Bisa tolong jelaskan kembali?"
)
FALLBACK_GENERIC = "Terima kasih. Bisa ceritakan lebih lanjut tentang properti Anda?"

_NEXT_QUESTION_SYSTEM = """\
You are a friendly assistant conducting a hospitality business assessment in \
Bahasa Indonesia. Ask exactly ONE natural follow-up question that helps collect \
the most important missing field. Do not repeat a question already asked, keep \
it conversational, and adapt to what the user has already said. Reply with the \
question text only, in Bahasa Indonesia.
"""


class ChatService:
    def __init__(
        self,
        db: Session,
        openai_service: OpenAIService | None = None,
        assessment_service: AssessmentService | None = None,
        extraction_service: ExtractionService | None = None,
        state_service: StateService | None = None,
    ) -> None:
        self.db = db
        self.openai = openai_service or OpenAIService()
        self.state = state_service or StateService(self.openai)
        self.assessments = assessment_service or AssessmentService(db, self.state)
        self.extraction = extraction_service or ExtractionService(self.openai)

    def handle_message(self, assessment_id: uuid.UUID, message: str) -> ChatResponse:
        """Process one user turn and return the assistant reply.

        Raises :class:`AssessmentNotFound` if the id is unknown.
        """
        assessment = self.assessments.get(assessment_id)
        if assessment is None:
            raise AssessmentNotFound(str(assessment_id))

        # 1. Persist the user's message.
        self._add_message(assessment_id, ConversationRole.USER, message)

        # 2 + 3. Extract fields and merge them in (extraction may fail).
        current_state = self.assessments.to_state_dict(assessment.data)
        extraction_failed = False
        try:
            extracted = self.extraction.extract(message, current_state)
        except OpenAIServiceError:
            extracted = {}
            extraction_failed = True

        if extracted:
            assessment = self.assessments.update_data(assessment_id, extracted)

        # 4. Recompute state.
        state = self.assessments.to_state_dict(assessment.data)
        missing = self.state.missing_fields(state)
        completion = assessment.completion_percentage
        stage = self.state.current_stage(state)

        # 5. Decide the reply.
        if extraction_failed:
            reply = FALLBACK_REPHRASE
        elif not missing:
            reply = CLOSING_MESSAGE
            self._mark_completed(assessment)
            completion = assessment.completion_percentage
            stage = "COMPLETE"
        else:
            try:
                reply = self._next_question(assessment_id, state, missing)
            except OpenAIServiceError:
                reply = FALLBACK_GENERIC

        # 6. Persist the assistant reply and return.
        self._add_message(assessment_id, ConversationRole.ASSISTANT, reply)
        return ChatResponse(reply=reply, completion_percentage=completion, next_stage=stage)

    def history(self, assessment_id: uuid.UUID) -> list[ConversationMessage]:
        """Return the ordered conversation history for an assessment."""
        rows = self.db.scalars(
            select(Conversation)
            .where(Conversation.assessment_id == assessment_id)
            .order_by(Conversation.created_at, Conversation.id)
        ).all()
        return [ConversationMessage(role=row.role, message=row.message) for row in rows]

    # -- internals -------------------------------------------------------------

    def _add_message(
        self, assessment_id: uuid.UUID, role: ConversationRole, message: str
    ) -> None:
        self.db.add(Conversation(assessment_id=assessment_id, role=role, message=message))
        self.db.commit()

    def _mark_completed(self, assessment) -> None:
        assessment.status = AssessmentStatus.COMPLETED
        assessment.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(assessment)

    def _next_question(self, assessment_id: uuid.UUID, state: dict, missing: list[str]) -> str:
        transcript = "\n".join(
            f"{m.role.value}: {m.message}" for m in self.history(assessment_id)
        )
        user_prompt = (
            f"Collected so far (JSON-ish): {state}\n"
            f"Missing required fields: {', '.join(missing)}\n\n"
            f"Conversation so far:\n{transcript}"
        )
        return self.openai.complete_text(_NEXT_QUESTION_SYSTEM, user_prompt, temperature=0.5)
