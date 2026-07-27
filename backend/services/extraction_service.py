"""Extraction service — Prompt 1 (Information Extraction).

Config-driven: the allowed fields, their descriptions/enum options, and the
injected ``knowledge``/``style``/``language`` all come from a
:class:`PipelineConfig`. The service returns fields in the config's vocabulary
(uncoerced); coercion to columns/JSON is done by ``FieldMapper``.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.pipeline import DEFAULT_CONFIG, FieldMapper, PipelineConfig
from backend.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

_BASE_INSTRUCTIONS = """
You are an information extraction engine for a structured business assessment.

Your ONLY job is to extract structured information from the user's latest message.

General Rules

- Extract every allowed field that the user's latest message answers.
- A field is considered answered even if the answer is negative, uncertain, incomplete, or indicates something does not yet exist.
- Never invent information.
- Never guess.
- Never infer facts that are not supported by the user's latest message.
- Ignore greetings, filler conversation, jokes, acknowledgements, and unrelated discussion.
- Normalize wording while preserving meaning.
- Extract as many fields as possible from a single message.
- Return ONLY the fields that are new or explicitly corrected.

Negative answers are VALID answers

The following kinds of responses should STILL populate the corresponding field:

- belum ada
- tidak ada
- belum punya
- belum mulai
- belum ditentukan
- belum yakin
- masih dipikirkan
- tidak tahu
- belum kepikiran
- similar expressions

Do NOT leave a field empty simply because the answer is negative.

Only omit a field if the user provides absolutely no information related to that field.

Enum Fields

- Return EXACTLY one of the allowed enum values.
- Never invent enum values.

Output

Return ONLY a JSON object.

If nothing can be extracted, return {}.
"""


class ExtractionService:
    def __init__(
        self,
        openai_service: OpenAIService | None = None,
        config: PipelineConfig | None = None,
    ) -> None:
        self.openai = openai_service or OpenAIService()
        self.config = config or DEFAULT_CONFIG
        self._mapper = FieldMapper(self.config)
        self._allowed = self._mapper.known_input_keys()

    def extract(self, user_message: str, current_state: dict) -> dict:
        """Return structured fields extracted from the latest user message."""

        raw = self.openai.complete_json(
            self._system_prompt(),
            self._user_prompt(user_message, current_state),
            temperature=0,
        )

        cleaned = self._clean(raw)

        logger.debug("=" * 60)
        logger.debug("Extraction")
        logger.debug("User Message: %s", user_message)
        logger.debug("Current State: %s", current_state)
        logger.debug("Raw Response: %s", raw)
        logger.debug("Cleaned Response: %s", cleaned)
        logger.debug("=" * 60)

        return cleaned

    # ------------------------------------------------------------------
    # Prompt Building
    # ------------------------------------------------------------------

    def _system_prompt(self) -> str:
        lines = [_BASE_INSTRUCTIONS]

        if self.config.knowledge:
            lines.append("\nBusiness Context")
            lines.append(self.config.knowledge)

        if self.config.style:
            lines.append("\nAssistant Persona")
            lines.append(self.config.style)

        lines.append(f"\nAssessment Language: {self.config.language}")

        lines.append("\nAllowed Fields")

        for field in self.config.fields:
            lines.append(f"\nField: {field.name}")
            lines.append(f"Type: {field.type}")

            if field.description:
                lines.append(f"Description: {field.description}")

            if field.enum_options:
                lines.append(
                    "Allowed Values: "
                    + ", ".join(field.enum_options)
                )

        return "\n".join(lines)

    def _user_prompt(
        self,
        user_message: str,
        current_state: dict,
    ) -> str:

        if current_state:
            current = "\n".join(
                f"- {key}: {value}"
                for key, value in current_state.items()
            )
        else:
            current = "(No information collected yet)"

        return f"""
Current Assessment State

{current}

{self._branch_hint(current_state)}

Instructions

- Extract NEW information from the latest user message.
- Do not remove existing values.
- Do not overwrite existing values unless the user explicitly corrects them.
- If the user answers a field negatively (for example "belum ada", "tidak tahu", "belum ditentukan"), treat it as a VALID answer.
- If no structured information is present, return {{}}.

Latest User Message

{user_message}
"""

    def _branch_hint(self, current_state: dict) -> str:
        """Guide the model toward fields relevant to the current business stage."""

        stage = current_state.get("business_stage")

        if not stage:
            return ""

        relevant = [
            field
            for field in self.config.fields
            if field.required_when
            and stage in field.required_when.get("business_stage", [])
        ]

        if not relevant:
            return ""

        lines = [
            f"Current Business Stage: {stage}",
            "",
            "Stage-specific fields:",
        ]

        for field in relevant:
            lines.append(
                f"- {field.name}: {field.description or 'No description'}"
            )

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Cleaning
    # ------------------------------------------------------------------

    def _clean(self, raw: dict) -> dict[str, Any]:
        cleaned: dict[str, Any] = {}

        for key, value in (raw or {}).items():
            if key not in self._allowed:
                continue

            if value is None:
                continue

            if isinstance(value, str) and not value.strip():
                continue

            if isinstance(value, (list, dict)) and len(value) == 0:
                continue

            cleaned[key] = value

        return cleaned