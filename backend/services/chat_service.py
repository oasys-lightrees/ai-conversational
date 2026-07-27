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
from backend.pipeline import DEFAULT_CONFIG, PipelineConfig
from backend.schemas.chat import ChatResponse, ConversationMessage
from backend.services.assessment_service import AssessmentNotFound, AssessmentService
from backend.services.extraction_service import ExtractionService
from backend.services.openai_service import OpenAIService, OpenAIServiceError
from backend.services.state_service import StateService

SECTION_ORDER = [
    "CLIENT",
    "PROPERTY",
    "BUSINESS",
    "CHALLENGES",
    "GOALS",
]
# Localized static copy (used when no model call is made). Keyed by config language.
_STATIC = {
    "id": {
        "closing": (
            "Terima kasih! Semua informasi yang dibutuhkan sudah terkumpul. "
            "Kami akan menyiapkan laporan asesmen Anda."
        ),
        "rephrase": (
            "Maaf, saya belum sepenuhnya menangkap informasinya. "
            "Bisa tolong jelaskan kembali?"
        ),
        "generic": "Terima kasih. Bisa ceritakan lebih lanjut tentang properti Anda?",
    },
    "en": {
        "closing": (
            "Thank you! We have all the information we need. "
            "We'll prepare your assessment report."
        ),
        "rephrase": "Sorry, I didn't quite catch that. Could you rephrase?",
        "generic": "Thank you. Could you tell me more about your property?",
    },
}

# Backwards-compatible constants (default language) for tests/importers.
CLOSING_MESSAGE = _STATIC["id"]["closing"]
FALLBACK_REPHRASE = _STATIC["id"]["rephrase"]
FALLBACK_GENERIC = _STATIC["id"]["generic"]


class ChatService:
    def __init__(
        self,
        db: Session,
        openai_service: OpenAIService | None = None,
        assessment_service: AssessmentService | None = None,
        extraction_service: ExtractionService | None = None,
        state_service: StateService | None = None,
        config: PipelineConfig | None = None,
    ) -> None:
        self.db = db
        self.config = config or DEFAULT_CONFIG
        self.openai = openai_service or OpenAIService()
        self.state = state_service or StateService(self.openai, config=self.config)
        self.assessments = assessment_service or AssessmentService(db, self.state, self.config)
        self.extraction = extraction_service or ExtractionService(self.openai, self.config)

    def _static(self, key: str) -> str:
        return _STATIC.get(self.config.language, _STATIC["id"])[key]

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
            reply = self._static("rephrase")
        elif not missing:
            reply = self._static("closing")
            self._mark_completed(assessment)
            completion = assessment.completion_percentage
            stage = "COMPLETE"
        else:
            try:
                reply = self._next_question(assessment_id, state, missing)
            except OpenAIServiceError:
                reply = self._static("generic")

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

    def _next_question_system(self) -> str:
        lines = [
            "You are LIA (Lightrees Intelligence Assistant), conducting a structured business assessment.",

            "Your objective is to collect all REQUIRED assessment fields through a natural conversation.",

            "Rules:",
            "- Ask EXACTLY ONE question at a time.",
            "- Ask ONLY about the missing required fields provided.",
            "- Prefer broad questions that can fill multiple missing fields.",
            "- Do NOT ask questions unrelated to the missing required fields.",
            "- Do NOT repeat questions if the user has already provided enough information.",
            "- If the user answers 'tidak tahu', 'belum ada', 'belum kepikiran', 'tidak yakin', or similar, treat it as a valid answer and continue to another field.",
            "- Do NOT investigate indefinitely or keep asking follow-up questions about the same topic.",
            "- Only ask a follow-up question if the previous answer is truly insufficient to fill a required field.",
            "- Do NOT invent new topics or additional assessment questions.",
            "- Keep the conversation concise and efficient.",

            "Response format:",
            "- Briefly acknowledge the user's previous answer when appropriate.",
            "- Then ask ONE natural question.",
            "- Do NOT provide recommendations or explanations during the assessment.",
            "- Reply in one or two short sentences only.",
        ]

        if self.config.knowledge:
            lines.append(f"\nDomain Knowledge:\n{self.config.knowledge}")

        if self.config.style:
            lines.append(f"\nPersona:\n{self.config.style}")

        lines.append(f"\nRespond in language: {self.config.language}.")

        return "\n".join(lines)

    def _next_question(
            self,
            assessment_id: uuid.UUID,
            state: dict,
            missing: list[str],
    ) -> str:
        field_map = {f.name: f for f in self.config.fields}

        def section_priority(section: str) -> int:
            try:
                return SECTION_ORDER.index(section)
            except ValueError:
                return len(SECTION_ORDER)

        # Collected information
        collected = [
            f"✓ {field.label}: {state[field.name]}"
            for field in self.config.fields
            if field.name in state
        ]

        # Missing fields ordered by conversation flow
        missing_fields = sorted(
            (field_map[name] for name in missing),
            key=lambda field: (
                section_priority(field.section),
                self.config.fields.index(field),
            ),
        )

        # Group missing fields by section
        grouped_missing: dict[str, list[str]] = {}

        for field in missing_fields:
            grouped_missing.setdefault(field.section, []).append(
                (
                    f"• {field.label}\n"
                    f"  Description: {field.description or 'No description'}"
                )
            )

        missing_text = []

        for section in SECTION_ORDER:
            if section not in grouped_missing:
                continue

            missing_text.append(f"=== {section} ===")
            missing_text.extend(grouped_missing[section])
            missing_text.append("")

        transcript = "\n".join(
            f"{m.role.value}: {m.message}"
            for m in self.history(assessment_id)
        )

        user_prompt = f"""
    Collected Information

    {chr(10).join(collected) if collected else "None"}

    Missing Required Fields

    {chr(10).join(missing_text)}

    Conversation History

    {transcript}

    Generate the next question.
    """
        print("=" * 80)
        print("SYSTEM PROMPT")
        print("=" * 80)
        print(self._next_question_system())

        print("=" * 80)
        print("CURRENT STATE")
        print("=" * 80)
        print(state)

        print("=" * 80)
        print("MISSING FIELDS")
        print("=" * 80)
        print(missing)

        print("=" * 80)
        print("ALL CONFIG FIELDS")
        print("=" * 80)
        print([f.name for f in self.config.fields])

        print("=" * 80)
        print("USER PROMPT")
        print("=" * 80)
        print(user_prompt)

        print("=" * 80)
        print("END PROMPT")
        print("=" * 80)
        return self.openai.complete_text(
            self._next_question_system(),
            user_prompt,
            temperature=0.2,
        )