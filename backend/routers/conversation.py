"""Conversation history endpoint."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.chat import ConversationMessage
from backend.services.chat_service import ChatService

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.get("/{assessment_id}", response_model=list[ConversationMessage])
def get_conversation(
    assessment_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[ConversationMessage]:
    """Return the conversation history for an assessment."""
    service = ChatService(db)
    if service.assessments.get(assessment_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    return service.history(assessment_id)
