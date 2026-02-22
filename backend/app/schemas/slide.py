import re
from typing import Literal

from pydantic import BaseModel, field_validator

# Slide types matching frontend
SlideType = Literal[
    "cover",
    "content",
    "quote",
    "list-item",
    "cta",
    "stat",
    "comparison",
    "steps",
    "feature",
    "testimonial",
    "image-full",
    "bullet-list",
    "big-text",
    "code",
]

# Layout types
SlideLayout = Literal["centered", "left", "split-left", "split-right", "minimal"]

# Font size options
FontSize = Literal["xs", "small", "medium", "large", "xl"]

# Image size options
ImageSize = Literal["small", "medium", "large"]


class DisplaySettings(BaseModel):
    """Display settings for a presentation (persisted)."""
    showBadge: bool = True
    showPageNumber: bool = True
    titleSize: FontSize = "medium"
    bodySize: FontSize = "medium"
    layout: SlideLayout = "centered"


class StepItem(BaseModel):
    title: str
    description: str | None = None
    icon: str | None = None


class ComparisonSide(BaseModel):
    title: str
    items: list[str] = []


class ComparisonData(BaseModel):
    left: ComparisonSide | None = None
    right: ComparisonSide | None = None


class Slide(BaseModel):
    id: str
    type: SlideType
    number: int | None = None
    title: str | None = None
    subtitle: str | None = None
    body: str | None = None
    highlights: list[str] | None = None  # Multiple words/phrases to highlight
    image: str | None = None  # Base64 or URL
    icon: str | None = None  # Lucide icon name
    ctaText: str | None = None
    # Per-slide display overrides
    layout: SlideLayout | None = None
    titleSize: FontSize | None = None
    bodySize: FontSize | None = None
    imageSize: ImageSize | None = None
    # Advanced slide type fields
    statValue: str | None = None
    statLabel: str | None = None
    steps: list[StepItem] | None = None
    comparison: ComparisonData | None = None
    avatar: str | None = None
    authorRole: str | None = None
    bullets: list[str] | None = None
    codeContent: str | None = None
    codeLanguage: str | None = None


# Hex color regex pattern
HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


class SlideTheme(BaseModel):
    id: str
    name: str
    background: str
    backgroundSecondary: str | None = None  # For gradients or split backgrounds
    accent: str
    accentSecondary: str | None = None  # For multi-color accents
    text: str
    textSecondary: str
    borderColor: str
    headerBg: str | None = None  # For split header style
    # Typography
    headingFont: str | None = None  # e.g., 'Playfair Display'
    bodyFont: str | None = None  # e.g., 'Inter'
    # Style settings
    fontStyle: str | None = None  # 'modern', 'serif', 'bold', 'mono'
    backgroundStyle: str | None = None  # 'solid', 'noise', 'dots', 'grid', 'paper', 'split'
    borderStyle: str | None = None  # 'accent', 'none', 'thin', 'thick'
    # Logo settings
    logoPosition: str | None = None  # 'top-left', 'top-right', 'bottom-left', 'bottom-right'
    logoSize: str | None = None  # 'small', 'medium', 'large'
    showLogo: bool | None = None
    showLogoOnCoverOnly: bool | None = None
    # Metadata (optional, for saved themes)
    isPreset: bool | None = None
    createdAt: str | None = None
    updatedAt: str | None = None

    @field_validator(
        "background",
        "accent",
        "text",
        "textSecondary",
        "borderColor",
        mode="before",
    )
    @classmethod
    def validate_required_colors(cls, v: str) -> str:
        if not v or not HEX_COLOR_PATTERN.match(v):
            raise ValueError(f"Invalid hex color: {v}. Must be in format #RRGGBB")
        return v

    @field_validator(
        "backgroundSecondary",
        "accentSecondary",
        "headerBg",
        mode="before",
    )
    @classmethod
    def validate_optional_colors(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not HEX_COLOR_PATTERN.match(v):
            raise ValueError(f"Invalid hex color: {v}. Must be in format #RRGGBB")
        return v
