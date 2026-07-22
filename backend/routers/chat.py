"""Chat endpoint: one conversation turn."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.assessment_service import AssessmentNotFound
from backend.services.chat_service import ChatService

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """Process a single conversation turn."""
    try:
        return ChatService(db).handle_message(request.assessment_id, request.message)
    except AssessmentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
