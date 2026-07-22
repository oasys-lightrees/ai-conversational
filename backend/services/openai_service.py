"""OpenAI API wrapper.

Responsible for managing OpenAI calls, prompt selection, response parsing, and
error handling. This is a scaffold: the client is wired up, but the individual
prompt calls are left unimplemented.
"""

from __future__ import annotations

from openai import OpenAI

from backend.config import settings


class OpenAIService:
    """Thin wrapper around the OpenAI client."""

    def __init__(self) -> None:
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(api_key=settings.openai_api_key)
        return self._client

    @property
    def model(self) -> str:
        return settings.openai_model

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        """Call the model and return a parsed JSON object.

        TODO: implement the chat-completions call with JSON response format and
        parse the result. See ``docs/05-prompt-design.MD``.
        """
        raise NotImplementedError

    def complete_text(self, system_prompt: str, user_prompt: str) -> str:
        """Call the model and return a plain-text completion.

        TODO: implement the chat-completions call.
        """
        raise NotImplementedError
