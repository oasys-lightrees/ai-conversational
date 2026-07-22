"""Tests for OpenAIService (no network — the SDK client is faked).

Verifies prompt/kwargs assembly, JSON parsing, and that every failure mode is
normalized to OpenAIServiceError.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from openai import OpenAIError

from backend.services.openai_service import OpenAIService, OpenAIServiceError


class _FakeCompletions:
    def __init__(self, content=None, exc=None, capture=None):
        self._content = content
        self._exc = exc
        self._capture = capture

    def create(self, **kwargs):
        if self._capture is not None:
            self._capture.update(kwargs)
        if self._exc is not None:
            raise self._exc
        message = SimpleNamespace(content=self._content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _service(content=None, exc=None, capture=None) -> OpenAIService:
    svc = OpenAIService()
    # Inject a fake client so no API key or network is needed.
    svc._client = SimpleNamespace(
        chat=SimpleNamespace(completions=_FakeCompletions(content, exc, capture))
    )
    return svc


def test_complete_json_parses_object():
    svc = _service(content='{"property_type": "Villa", "total_units": 12}')
    assert svc.complete_json("sys", "user") == {"property_type": "Villa", "total_units": 12}


def test_complete_json_sets_json_response_format():
    capture: dict = {}
    svc = _service(content="{}", capture=capture)
    svc.complete_json("sys", "user")
    assert capture["response_format"] == {"type": "json_object"}
    assert capture["messages"][0]["role"] == "system"
    assert capture["messages"][1]["content"] == "user"


def test_complete_json_invalid_json_raises():
    svc = _service(content="not json at all")
    with pytest.raises(OpenAIServiceError):
        svc.complete_json("sys", "user")


def test_complete_json_non_object_raises():
    svc = _service(content="[1, 2, 3]")
    with pytest.raises(OpenAIServiceError):
        svc.complete_json("sys", "user")


def test_complete_text_returns_stripped_text():
    svc = _service(content="  Halo dunia  ")
    assert svc.complete_text("sys", "user") == "Halo dunia"


def test_complete_text_omits_json_response_format():
    capture: dict = {}
    svc = _service(content="hi", capture=capture)
    svc.complete_text("sys", "user")
    assert "response_format" not in capture


def test_temperature_override_passed_through():
    capture: dict = {}
    svc = _service(content="{}", capture=capture)
    svc.complete_json("sys", "user", temperature=0.9)
    assert capture["temperature"] == 0.9


def test_sdk_error_normalized():
    svc = _service(exc=OpenAIError("boom"))
    with pytest.raises(OpenAIServiceError):
        svc.complete_text("sys", "user")


def test_empty_content_raises():
    svc = _service(content=None)
    with pytest.raises(OpenAIServiceError):
        svc.complete_text("sys", "user")
