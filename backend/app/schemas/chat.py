from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    slides_context: list[dict] | None = None  # Current slides state
    enable_search: bool = Field(default=True)


class SlideSuggestion(BaseModel):
    slideIndex: int
    type: Literal["modify", "add", "delete", "reorder"]
    field: str | None = None
    currentValue: str | None = None
    suggestedValue: str | None = None
    reason: str


class Citation(BaseModel):
    url: str
    title: str | None = None


class ChatMessageResponse(BaseModel):
    id: UUID
    presentation_id: UUID
    role: Literal["user", "assistant"]
    content: str
    suggestions: list[SlideSuggestion] | None = None
    suggestion_status: dict | None = None
    search_results: list[dict] | None = None
    citations: list[Citation] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessageResponse]
    total: int


class SuggestionAcceptRequest(BaseModel):
    pass  # No body needed, just the URL params


class SuggestionAcceptResponse(BaseModel):
    success: bool
    updated_slide: dict | None = None
    message: str | None = None


class ScreenshotUploadResponse(BaseModel):
    id: UUID
    session_id: str
    filename: str
    url: str
    ai_description: str | None = None
    order_index: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ScreenshotListResponse(BaseModel):
    screenshots: list[ScreenshotUploadResponse]
    session_id: str
