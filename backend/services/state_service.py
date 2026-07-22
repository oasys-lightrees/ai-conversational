"""State service — Prompt 2 (Missing Field Detection) and stage tracking.

Tracks the current conversation stage, identifies missing required fields, and
prevents duplicate questions. See ``docs/05-prompt-design.MD``.
"""

from __future__ import annotations

from backend.services.openai_service import OpenAIService


class StateService:
    def __init__(self, openai_service: OpenAIService | None = None) -> None:
        self.openai = openai_service or OpenAIService()

    def missing_fields(self, current_state: dict) -> list[str]:
        """Return the list of required fields still missing.

        TODO: implement required-field validation / detection.
        """
        raise NotImplementedError

    def completion_percentage(self, current_state: dict) -> int:
        """Return assessment completion as an integer percentage.

        TODO: implement completion calculation.
        """
        raise NotImplementedError

    def current_stage(self, current_state: dict) -> str:
        """Return the current conversation stage identifier.

        TODO: implement stage detection.
        """
        raise NotImplementedError
