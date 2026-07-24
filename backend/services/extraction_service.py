"""Extraction service — Prompt 1 (Information Extraction).

Config-driven: the allowed fields, their descriptions/enum options, and the
injected ``knowledge``/``style``/``language`` all come from a
:class:`PipelineConfig`. The service returns fields in the config's vocabulary
(uncoerced); coercion to columns/JSON is done by ``FieldMapper``. See
``docs/05`` and ``docs/11-pipeline-config.MD``.
"""

from __future__ import annotations

from typing import Any

from backend.pipeline import DEFAULT_CONFIG, FieldMapper, PipelineConfig
from backend.services.openai_service import OpenAIService

_BASE_INSTRUCTIONS = (
    "You extract structured business information from a property owner's "
    "message for an assessment. Extract as many of the allowed fields as the "
    "message clearly supports; ignore filler; normalize values; never invent "
    "information. For enum fields, return exactly one of the listed options. "
    "Return ONLY a JSON object whose keys are from the allowed field list; omit "
    "anything not mentioned. If nothing can be extracted, return {}."
)


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
        """Return structured fields extracted from ``user_message`` (uncoerced)."""
        raw = self.openai.complete_json(
            self._system_prompt(), self._user_prompt(user_message, current_state), temperature=0
        )
        return self._clean(raw)

    # -- prompt building -------------------------------------------------------

    def _system_prompt(self) -> str:
        lines = [_BASE_INSTRUCTIONS]
        if self.config.knowledge:
            lines.append(f"\nContext:\n{self.config.knowledge}")
        if self.config.style:
            lines.append(f"\nStyle:\n{self.config.style}")
        lines.append(f"\nRespond using field names in English. Language: {self.config.language}.")
        lines.append("\nAllowed fields:")
        for field in self.config.fields:
            options = f" [{', '.join(field.enum_options)}]" if field.enum_options else ""
            hint = f" — {field.description}" if field.description else ""
            lines.append(f"- {field.name} ({field.type}){options}{hint}")
        return "\n".join(lines)

    def _user_prompt(self, user_message: str, current_state: dict) -> str:
        already = ", ".join(sorted(current_state)) if current_state else "(none)"
        return (
            f"Already collected fields (do not re-ask, but you may refine): {already}\n"
            f"{self._branch_hint(current_state)}"
            f"User message:\n{user_message}"
        )

    def _branch_hint(self, current_state: dict) -> str:
        """Nudge the model toward fields relevant to the active business stage."""
        stage = current_state.get("business_stage")
        if not stage:
            return ""
        relevant = [
            field.name
            for field in self.config.fields
            if field.required_when
            and stage in field.required_when.get("business_stage", [])
        ]
        if not relevant:
            return ""
        return f"Active business stage is {stage}; relevant fields: {', '.join(relevant)}\n"

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
