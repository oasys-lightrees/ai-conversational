"""Extraction service — Prompt 1 (Information Extraction).

Extracts structured business fields from a user message. See
``docs/05-prompt-design.MD``.
"""

from __future__ import annotations

from backend.services.openai_service import OpenAIService


class ExtractionService:
    def __init__(self, openai_service: OpenAIService | None = None) -> None:
        self.openai = openai_service or OpenAIService()

    def extract(self, user_message: str, current_state: dict) -> dict:
        """Return structured fields extracted from ``user_message``.

        TODO: build the extraction prompt and call the model.
        """
        raise NotImplementedError
