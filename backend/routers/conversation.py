"""Conversation history endpoint."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.chat import ConversationMessage

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.get("/{assessment_id}", response_model=list[ConversationMessage])
def get_conversation(
    assessment_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[ConversationMessage]:
    """Return the conversation history for an assessment. TODO: implement."""
    raise NotImplementedError
