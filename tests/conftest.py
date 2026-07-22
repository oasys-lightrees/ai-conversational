"""Shared test fixtures.

Per Decision D2 in ``docs/10-implementation-plan.MD``, DB-backed tests run
against Postgres (the Compose ``db`` service), not SQLite, because
``AssessmentData`` relies on ``JSONB``/``UUID`` column types. Set
``TEST_DATABASE_URL`` to override the connection.

Pure tests (field mapping, state service) need no fixtures and run regardless.
"""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# Importing the models package registers every table on Base.metadata.
import backend.models  # noqa: F401
from backend.database import Base

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://assessment:assessment@localhost:5432/assessment",
    ),
)


class FakeOpenAIService:
    """Deterministic stand-in for OpenAIService (for Phases 2–4 tests).

    Returns canned values so extraction/state/chat/report can be tested with no
    network and no API key.
    """

    def __init__(self, json_result: dict | None = None, text_result: str = "") -> None:
        self.json_result = json_result or {}
        self.text_result = text_result
        self.model = "fake-model"

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        return dict(self.json_result)

    def complete_text(self, system_prompt: str, user_prompt: str) -> str:
        return self.text_result


@pytest.fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
    eng = create_engine(TEST_DATABASE_URL, future=True)
    yield eng
    eng.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Generator[Session, None, None]:
    # Fresh schema per test for isolation (handful of tests; simple and robust).
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    session = session_local()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session):
    """FastAPI TestClient wired to the test session."""
    from fastapi.testclient import TestClient

    from backend.database import get_db
    from backend.main import app

    def _override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
