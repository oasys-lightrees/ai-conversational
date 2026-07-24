"""State service — required-field detection, completion, and stage tracking.

Config-driven and rule-based (no API key). Required fields, conditional/branch
requirements, completion percentage, and the conversation stage are all derived
from the :class:`PipelineConfig`'s field specs. See ``docs/11-pipeline-config.MD``.

Operates on the flat ``dict`` from ``AssessmentService.to_state_dict`` — column
values (enums as their string value) plus the JSON fields flattened in, with
absent fields omitted.
"""

from __future__ import annotations

from backend.pipeline import DEFAULT_CONFIG, PipelineConfig
from backend.pipeline.config import FieldSpec
from backend.services.openai_service import OpenAIService


def _present(state: dict, key: str) -> bool:
    """True if ``key`` holds a meaningful value (0 counts; ""/[] do not)."""
    value = state.get(key)
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
    return True


class StateService:
    def __init__(
        self,
        openai_service: OpenAIService | None = None,
        config: PipelineConfig | None = None,
    ) -> None:
        self.openai = openai_service or OpenAIService()
        self.config = config or DEFAULT_CONFIG

    def _required(self, state: dict) -> list[FieldSpec]:
        return [field for field in self.config.fields if field.is_required(state)]

    def missing_fields(self, current_state: dict) -> list[str]:
        """Required fields (always + active conditional) not yet present."""
        return [f.name for f in self._required(current_state) if not _present(current_state, f.name)]

    def completion_percentage(self, current_state: dict) -> int:
        """Percentage of required fields present, as an integer 0–100."""
        required = self._required(current_state)
        if not required:
            return 0
        present = sum(1 for f in required if _present(current_state, f.name))
        return int(round(present / len(required) * 100))

    def current_stage(self, current_state: dict) -> str:
        """The section the conversation is currently working through.

        Sections are walked in field order. A "gating" section (one containing a
        required or conditionally-required field) is returned while it still has
        a currently-required field missing; an optional section is returned while
        it has no field present. When nothing is left, returns ``"COMPLETE"``.
        """
        for section in self._sections():
            fields = [f for f in self.config.fields if f.section == section]
            gating = any(f.required or f.required_when for f in fields)
            if gating:
                if any(f.is_required(current_state) and not _present(current_state, f.name) for f in fields):
                    return section
            elif not any(_present(current_state, f.name) for f in fields):
                return section
        return "COMPLETE"

    def _sections(self) -> list[str]:
        sections: list[str] = []
        for field in self.config.fields:
            if field.section and field.section not in sections:
                sections.append(field.section)
        return sections
