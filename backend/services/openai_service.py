"""OpenAI API wrapper.

The single choke point for every AI call in the app (extraction, missing-field
detection, question generation, report). It normalizes all failure modes —
network, timeout, HTTP error, empty response, unparseable JSON — into one
exception type, :class:`OpenAIServiceError`, so callers (notably ``ChatService``)
can implement their partial-failure policy against a single class. Retries and
per-request timeout are configured from ``settings`` (see ``docs/10``).
"""

from __future__ import annotations

import json

from openai import OpenAI, OpenAIError

from backend.config import settings


class OpenAIServiceError(Exception):
    """Any failure while calling OpenAI or parsing its response."""


class OpenAIService:
    """Thin wrapper around the OpenAI client."""

    def __init__(self) -> None:
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                api_key=settings.openai_api_key,
                max_retries=settings.openai_max_retries,
            )
        return self._client

    @property
    def model(self) -> str:
        return settings.openai_model

    def _chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        json_mode: bool,
        temperature: float | None,
    ) -> str:
        """Run one chat completion and return the raw message content.

        Wraps every SDK error in :class:`OpenAIServiceError`.
        """
        kwargs: dict = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": settings.openai_temperature if temperature is None else temperature,
            "timeout": settings.openai_timeout,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = self.client.chat.completions.create(**kwargs)
        except OpenAIError as exc:  # network, timeout, rate limit, HTTP error
            raise OpenAIServiceError(f"OpenAI request failed: {exc}") from exc

        content = response.choices[0].message.content
        if content is None:
            raise OpenAIServiceError("OpenAI returned empty content.")
        return content

    def complete_json(
        self, system_prompt: str, user_prompt: str, *, temperature: float | None = None
    ) -> dict:
        """Call the model in JSON mode and return the parsed object.

        Raises :class:`OpenAIServiceError` if the response is not a JSON object.
        """
        content = self._chat(
            system_prompt, user_prompt, json_mode=True, temperature=temperature
        )
        try:
            data = json.loads(content)
        except (json.JSONDecodeError, TypeError) as exc:
            raise OpenAIServiceError(f"OpenAI returned invalid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise OpenAIServiceError(
                f"OpenAI returned a JSON {type(data).__name__}, expected an object."
            )
        return data

    def complete_text(
        self, system_prompt: str, user_prompt: str, *, temperature: float | None = None
    ) -> str:
        """Call the model and return the plain-text completion (stripped)."""
        content = self._chat(
            system_prompt, user_prompt, json_mode=False, temperature=temperature
        )
        return content.strip()
