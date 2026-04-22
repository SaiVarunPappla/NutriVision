"""
NutriVision - Chat Models

Request/response models for AI chat endpoint.
"""

from pydantic import BaseModel, Field
from typing import Any, Optional


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question for AI chat")
    scan_context: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional scan result context from Android app"
    )
    user_profile: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional user profile context for personalization"
    )


class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI answer text")
    source: str = Field("fallback", description="Response source: gemini or fallback")
    used_scan_context: bool = Field(False, description="Whether scan context was provided")
    safety_note: Optional[str] = Field(
        "This is educational guidance, not medical diagnosis.",
        description="Safety reminder"
    )
