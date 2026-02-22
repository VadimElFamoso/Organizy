import re
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, field_validator

# Hex color validation
HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


def validate_hex_color(v: str) -> str:
    if not HEX_COLOR_PATTERN.match(v):
        raise ValueError(f"Invalid hex color: {v}. Must be in format #RRGGBB")
    return v


# ============ Theme Data (the actual theme colors/settings) ============

class ThemeData(BaseModel):
    """The actual theme configuration stored in theme_data JSON field."""
    background: str
    backgroundSecondary: str | None = None
    accent: str
    accentSecondary: str | None = None
    text: str
    textSecondary: str
    borderColor: str
    headerBg: str | None = None
    # Typography
    headingFont: str | None = None
    bodyFont: str | None = None
    # Style settings
    fontStyle: Literal["modern", "serif", "bold", "mono"] | None = None
    backgroundStyle: Literal["solid", "noise", "dots", "grid", "paper", "split"] | None = None
    borderStyle: Literal["none", "thin", "accent", "thick"] | None = None
    # Logo display settings (logos are global, display is per-theme)
    logoPosition: Literal["top-left", "top-right", "bottom-left", "bottom-right"] | None = None
    logoSize: Literal["small", "medium", "large"] | None = None
    showLogo: bool | None = None
    showLogoOnCoverOnly: bool | None = None

    @field_validator("background", "accent", "text", "textSecondary", "borderColor", mode="before")
    @classmethod
    def validate_required_colors(cls, v: str) -> str:
        return validate_hex_color(v)

    @field_validator("backgroundSecondary", "accentSecondary", "headerBg", mode="before")
    @classmethod
    def validate_optional_colors(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return validate_hex_color(v)


# ============ Theme CRUD Schemas ============

class ThemeBase(BaseModel):
    name: str
    theme_data: ThemeData


class ThemeCreate(ThemeBase):
    """Schema for creating a new theme."""
    pass


class ThemeUpdate(BaseModel):
    """Schema for updating a theme."""
    name: str | None = None
    theme_data: ThemeData | None = None
    is_default: bool | None = None


class ThemeResponse(ThemeBase):
    """Schema for theme response."""
    id: UUID
    user_id: UUID
    is_default: bool
    brand_kit_id: UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ThemeListResponse(BaseModel):
    """Schema for list of themes response with pagination."""
    themes: list[ThemeResponse]
    total: int
    page: int = 1
    limit: int = 50
    has_more: bool = False


# ============ Brand Kit Schemas ============

class LogoSettings(BaseModel):
    """Logo display settings."""
    position: Literal["top-left", "top-right", "bottom-left", "bottom-right"] = "top-left"
    size: Literal["small", "medium", "large"] = "medium"
    showOnAllSlides: bool = False
    showOnCoverOnly: bool = True


class BrandKitCreate(BaseModel):
    """Schema for creating a brand kit."""
    name: str = "My Brand"
    logo_settings: LogoSettings | None = None
    theme_id: UUID | None = None


class BrandKitUpdate(BaseModel):
    """Schema for updating a brand kit."""
    name: str | None = None
    logo_settings: LogoSettings | None = None
    theme_id: UUID | None = None


class BrandAssetResponse(BaseModel):
    """Schema for brand asset response."""
    id: UUID
    asset_type: str
    filename: str
    url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BrandKitResponse(BaseModel):
    """Schema for brand kit response."""
    id: UUID
    user_id: UUID
    name: str
    logo_settings: LogoSettings | None = None
    theme_id: UUID | None = None
    theme: ThemeResponse | None = None
    created_at: datetime
    updated_at: datetime
    assets: list[BrandAssetResponse] = []

    model_config = {"from_attributes": True}
