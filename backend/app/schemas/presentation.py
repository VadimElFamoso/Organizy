from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.slide import DisplaySettings, Slide, SlideTheme


class PresentationBase(BaseModel):
    title: str
    description: str | None = None


class PresentationCreate(PresentationBase):
    slides: list[Slide]
    theme: SlideTheme
    display_settings: DisplaySettings | None = None


class PresentationUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    slides: list[Slide] | None = None
    theme: SlideTheme | None = None
    display_settings: DisplaySettings | None = None


class PresentationResponse(PresentationBase):
    id: UUID
    slides: list[Slide]
    theme: SlideTheme
    display_settings: DisplaySettings | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PresentationListResponse(BaseModel):
    items: list[PresentationResponse]
    total: int
    page: int
    pages: int
