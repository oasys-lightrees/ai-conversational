"""Extraction service — Prompt 1 (Information Extraction).

Extracts structured business fields from one user message (``docs/05``). The
service returns fields in the *schema-doc vocabulary* (e.g. ``location``,
``property_type: "Villa"``); it deliberately does **not** coerce to columns or
enum members — that is the sole responsibility of ``field_mapping`` (the G4
resolution in ``docs/10``). Here we only: build the prompt, call the model in
JSON mode, drop null/empty values, and drop keys outside the accepted
vocabulary.

The allowed field list and enum options embedded in the prompt are derived from
``field_mapping`` so the prompt can never drift from what the mapper accepts.
"""

from __future__ import annotations

from typing import Any

from backend.models.enums import BusinessStage
from backend.services.field_mapping import ENUM_COLUMNS, known_input_fields
from backend.services.openai_service import OpenAIService
from backend.services.state_service import BRANCH_REQUIRED

_SYSTEM_INSTRUCTIONS = """\
You extract structured business information from a property owner's message for \
a hospitality assessment. The conversation is in Bahasa Indonesia; field names \
stay in English.

Rules:
- Extract as many of the allowed fields as the message clearly supports.
- Ignore conversational filler; never invent or guess missing information.
- Normalize values (e.g. "dua belas" -> 12). For enum fields, return exactly one \
of the listed options.
- Return ONLY a JSON object whose keys are from the allowed field list. Omit any \
field not mentioned. If nothing can be extracted, return {}.
"""


class ExtractionService:
    def __init__(self, openai_service: OpenAIService | None = None) -> None:
        self.openai = openai_service or OpenAIService()
        self._allowed = known_input_fields()

    def extract(self, user_message: str, current_state: dict) -> dict:
        """Return structured fields extracted from ``user_message``.

        Values are in schema-doc vocabulary and are cleaned but not coerced;
        pass them to ``field_mapping.map_extracted_to_columns`` for persistence.
        """
        system_prompt = self._system_prompt()
        user_prompt = self._user_prompt(user_message, current_state)
        # Deterministic extraction.
        raw = self.openai.complete_json(system_prompt, user_prompt, temperature=0)
        return self._clean(raw)

    # -- prompt building -------------------------------------------------------

    def _system_prompt(self) -> str:
        allowed = ", ".join(sorted(self._allowed))
        enum_lines = []
        for field, enum_cls in ENUM_COLUMNS.items():
            options = ", ".join(str(member.value) for member in enum_cls)
            enum_lines.append(f"- {field}: one of [{options}]")
        return (
            f"{_SYSTEM_INSTRUCTIONS}\n"
            f"Allowed fields: {allowed}\n\n"
            f"Enum fields and their allowed values:\n" + "\n".join(enum_lines)
        )

    def _user_prompt(self, user_message: str, current_state: dict) -> str:
        already = ", ".join(sorted(current_state)) if current_state else "(none)"
        hint = self._branch_hint(current_state)
        return (
            f"Already collected fields (do not re-ask, but you may refine): {already}\n"
            f"{hint}"
            f"User message:\n{user_message}"
        )

    def _branch_hint(self, current_state: dict) -> str:
        """Nudge the model toward the active branch's fields, if the stage is set."""
        stage_value = current_state.get("business_stage")
        if not stage_value:
            return ""
        try:
            stage = BusinessStage(stage_value)
        except ValueError:
            return ""
        fields = BRANCH_REQUIRED.get(stage)
        if not fields:
            return ""
        return f"Active business stage is {stage.value}; relevant fields: {', '.join(fields)}\n"

    # -- cleaning --------------------------------------------------------------

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
