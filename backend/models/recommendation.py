"""
NutriVision - Recommendation Models

Pydantic models for health recommendations generated after analysis.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal


class RecommendationItem(BaseModel):
    """A single recommendation or alert for the user."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "type": "warning",
            "title": "High Sodium Content",
            "message": "This product contains 20% of daily sodium intake. Consider low-sodium alternatives.",
            "severity": "medium"
        }
    })

    type: Literal["warning", "allergen_alert", "suggestion", "info"] = Field(
        ..., description="Recommendation category"
    )
    title: str = Field(..., description="Short title for the recommendation")
    message: str = Field(..., description="Detailed recommendation text")
    severity: Literal["high", "medium", "low"] = Field(
        "low", description="Severity level"
    )


class RecommendationResponse(BaseModel):
    """Full recommendation set for a scan result."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "recommendation_id": "rec_001",
            "scan_id": "scan_001",
            "user_id": "user_001",
            "recommendations": [
                {
                    "type": "allergen_alert",
                    "title": "Contains Gluten",
                    "message": "Wheat flour is a source of gluten. Avoid if gluten-intolerant.",
                    "severity": "high"
                },
                {
                    "type": "suggestion",
                    "title": "Try Whole Grains",
                    "message": "Replace refined flour with whole wheat flour for higher fiber.",
                    "severity": "low"
                }
            ]
        }
    })

    recommendation_id: Optional[str] = None
    scan_id: str = Field(..., description="Reference to the analyzed scan")
    user_id: str = Field(..., description="User who received these recommendations")
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    created_at: Optional[str] = None


class HistoryItem(BaseModel):
    """A scan history entry displayed in the history list."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "history_id": "hist_001",
            "user_id": "user_001",
            "scan_id": "scan_001",
            "product_name": "Chocolate Cookies",
            "scan_type": "image",
            "total_calories": 250.5,
            "health_score": 6.5,
            "allergens_count": 2,
            "created_at": "2026-04-15T12:30:00Z"
        }
    })

    history_id: Optional[str] = None
    user_id: str
    scan_id: str
    product_name: Optional[str] = "Unknown Product"
    scan_type: str = "text"
    total_calories: float = 0.0
    health_score: float = 0.0
    allergens_count: int = 0
    created_at: Optional[str] = None
