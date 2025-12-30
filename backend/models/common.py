"""Common/utility Pydantic models used across multiple features"""

from typing import Optional, List
from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    """Request for text-to-speech conversion."""
    text: str = Field(..., min_length=1, max_length=4096)
    voice: str = Field(default="onyx", pattern="^(alloy|echo|fable|onyx|nova|shimmer)$")


class SpeakRequest(BaseModel):
    """Request for text-to-speech."""
    text: str
    voice: str = "alloy"  # alloy, echo, fable, onyx, nova, shimmer


class ScreenshotExtractRequest(BaseModel):
    image: str  # Base64 encoded image


class ExtractedJob(BaseModel):
    title: str
    company: str
    status: Optional[str] = None
    date_applied: Optional[str] = None


class ScreenshotExtractResponse(BaseModel):
    jobs: List[ExtractedJob]
    message: Optional[str] = None


class FeedbackAcknowledgmentRequest(BaseModel):
    email: str
    name: Optional[str] = None
    feedback_type: str  # bug, feature_request, praise, ux_issue, general
    feedback_summary: str  # First ~100 chars of feedback
    current_page: Optional[str] = None  # What page they were on
    full_feedback: Optional[str] = None  # Full feedback text for admin
    conversation_context: Optional[str] = None  # Recent conversation for context
