from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.slide import Slide


class SlideGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    slide_count: int = Field(default=7, ge=3, le=15)
    style: Literal["tips", "quotes", "mixed"] = "tips"
    # Enhanced generation options
    session_id: str | None = Field(default=None, description="Links to uploaded screenshots")
    target_audience: str | None = Field(default=None, max_length=200)
    writing_style: str | None = Field(default=None, max_length=200)
    language: str = Field(default="French", max_length=50)
    enable_search: bool = Field(default=True, description="Enable web search for topic research")


class SlideGenerationResponse(BaseModel):
    slides: list[Slide]
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class GenerationHistoryResponse(BaseModel):
    id: UUID
    topic: str
    style: str
    slide_count: int
    presentation_id: UUID | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerationHistoryListResponse(BaseModel):
    items: list[GenerationHistoryResponse]
    total: int
    page: int
    pages: int


class TranslateRequest(BaseModel):
    slides: list[dict]
    target_language: str = Field(..., min_length=1, max_length=50)


class TranslateResponse(BaseModel):
    slides: list[dict]
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
