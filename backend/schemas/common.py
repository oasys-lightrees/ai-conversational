"""Shared response envelope schemas (see ``docs/08-api-design.MD``)."""

from typing import Any

from pydantic import BaseModel


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Any | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str = ""
    errors: list[Any] = []
