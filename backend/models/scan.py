"""
NutriVision - Scan Models

Pydantic models for scan requests, responses, and Firestore documents.
Supports both image-based and text-based ingredient analysis.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal
from models.ingredient import IngredientResponse
from models.nutrition import NutritionSummary, DietarySuitability
from models.recommendation import RecommendationItem


class TextScanRequest(BaseModel):
    """Request body for text-based ingredient analysis."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "text": "sugar, enriched wheat flour, palm oil, cocoa, soy lecithin, salt",
            "user_id": "demo_user_001",
            "product_name": "Chocolate Cookies"
        }
    })

    text: str = Field(
        ...,
        min_length=2,
        description="Raw ingredient text (comma-separated or from a label)"
    )
    user_id: str = Field(..., description="Firebase Auth UID of the user")
    product_name: Optional[str] = Field(None, description="Optional product name")


class ScanDocument(BaseModel):
    """Firestore document structure for a scan record."""
    scan_id: Optional[str] = None
    user_id: str
    scan_type: Literal["image", "text"] = "text"
    input_text: Optional[str] = None
    image_url: Optional[str] = None
    extracted_text: Optional[str] = None
    status: Literal["processing", "completed", "failed"] = "processing"
    created_at: Optional[str] = None


class ScanResponse(BaseModel):
    """Complete scan analysis response returned to the Android app."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "scan_id": "scan_001",
            "status": "completed",
            "scan_type": "text",
            "product_name": "Chocolate Cookies",
            "extracted_text": "sugar, enriched wheat flour, palm oil, cocoa",
            "ingredients": [
                {
                    "name": "sugar",
                    "normalized_name": "sugar",
                    "position": 1,
                    "usda_fdc_id": 174230,
                    "confidence": 0.95
                }
            ],
            "nutrition": {
                "total_calories": 250.5,
                "protein": {"value": 5.2, "unit": "g", "daily_pct": 10.4},
                "carbohydrates": {"value": 35.0, "unit": "g", "daily_pct": 12.7},
                "fat": {"value": 10.1, "unit": "g", "daily_pct": 15.5},
                "fiber": {"value": 2.1, "unit": "g", "daily_pct": 7.5},
                "sugar": {"value": 12.0, "unit": "g", "daily_pct": 24.0},
                "sodium": {"value": 480.0, "unit": "mg", "daily_pct": 20.0},
                "saturated_fat": {"value": 3.5, "unit": "g", "daily_pct": 17.5},
                "cholesterol": {"value": 15.0, "unit": "mg", "daily_pct": 5.0}
            },
            "allergens": ["gluten", "soy"],
            "dietary_suitability": {
                "is_vegetarian": True,
                "is_vegan": False,
                "is_gluten_free": False,
                "is_dairy_free": True,
                "is_keto_friendly": False,
                "is_nut_free": True
            },
            "health_score": 6.5,
            "recommendations": [
                {
                    "type": "warning",
                    "title": "High Sugar",
                    "message": "This product has high sugar content.",
                    "severity": "medium"
                }
            ],
            "status_message": "Branded match found via USDA FoodData Central."
        }
    })

    scan_id: str = Field(..., description="Unique scan identifier")
    status: str = Field("completed", description="Scan status")
    scan_type: str = Field("text", description="Type of scan performed (text, image, branded_text, branded_image)")
    product_name: Optional[str] = Field(None, description="Product name if provided or extracted")
    extracted_text: str = Field("", description="Raw text extracted or provided")
    ingredients: list[IngredientResponse] = Field(
        default_factory=list, description="Parsed ingredients"
    )
    nutrition: NutritionSummary = Field(
        default_factory=NutritionSummary, description="Nutrition breakdown"
    )
    allergens: list[str] = Field(
        default_factory=list, description="Detected allergens"
    )
    dietary_suitability: DietarySuitability = Field(
        default_factory=DietarySuitability, description="Diet compatibility"
    )
    health_score: float = Field(
        0.0, ge=0.0, le=10.0, description="Overall health score"
    )
    recommendations: list[RecommendationItem] = Field(
        default_factory=list, description="Personalized recommendations"
    )
    status_message: Optional[str] = Field(None, description="Optional message for client, e.g., if fallback was used")

