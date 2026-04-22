"""
NutriVision - Nutrition Models

Pydantic models for nutrition data, nutrient breakdowns,
and dietary suitability flags.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, List


class NutrientDetail(BaseModel):
    """Single nutrient measurement with daily value percentage."""
    value: float = Field(0.0, description="Nutrient amount")
    unit: str = Field("g", description="Measurement unit (g, mg, mcg)")
    daily_pct: float = Field(0.0, description="Percentage of daily recommended value")


class DietarySuitability(BaseModel):
    """Dietary classification flags for the analyzed food."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "is_vegetarian": True,
            "is_vegan": False,
            "is_gluten_free": False,
            "is_dairy_free": True,
            "is_keto_friendly": False,
            "is_nut_free": True
        }
    })

    is_vegetarian: bool = Field(False, description="Suitable for vegetarians")
    is_vegan: bool = Field(False, description="Suitable for vegans")
    is_gluten_free: bool = Field(False, description="Free from gluten")
    is_dairy_free: bool = Field(False, description="Free from dairy")
    is_keto_friendly: bool = Field(False, description="Suitable for keto diet")
    is_nut_free: bool = Field(False, description="Free from tree nuts and peanuts")


class NutritionSummary(BaseModel):
    """Aggregated nutrition data for all analyzed ingredients."""
    total_calories: float = Field(0.0, description="Total estimated calories")
    protein: NutrientDetail = Field(default_factory=NutrientDetail)
    carbohydrates: NutrientDetail = Field(default_factory=NutrientDetail)
    fat: NutrientDetail = Field(default_factory=NutrientDetail)
    fiber: NutrientDetail = Field(default_factory=NutrientDetail)
    sugar: NutrientDetail = Field(default_factory=NutrientDetail)
    sodium: NutrientDetail = Field(default_factory=NutrientDetail)
    saturated_fat: NutrientDetail = Field(default_factory=NutrientDetail)
    cholesterol: NutrientDetail = Field(default_factory=NutrientDetail)
    
    # New fields for overall scan result transparency
    overall_nutrition_source: Optional[str] = Field(None, description="Primary source for the overall nutrition data (e.g., 'USDA', 'Aggregated')")
    overall_matched_name: Optional[str] = Field(None, description="The exact product/ingredient name matched by the primary source or 'Aggregated Ingredients'")
    overall_matched_type: Optional[str] = Field(None, description="Type of match: 'branded_product', 'single_ingredient', 'aggregated_ingredients', 'estimated', 'no_match'")
    overall_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Overall confidence score for the nutrition data (0.0 to 1.0)")
    warning_messages: List[str] = Field(default_factory=list, description="List of warnings or uncertainties about the nutrition data")
    unresolved_ingredients: List[str] = Field(default_factory=list, description="List of original ingredient names that could not be confidently resolved")


class NutritionResult(BaseModel):
    """Complete nutrition analysis result stored in Firestore."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "result_id": "nr_001",
            "scan_id": "scan_001",
            "user_id": "user_001",
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
            "allergens_detected": ["gluten", "soy"],
            "dietary_suitability": {
                "is_vegetarian": True,
                "is_vegan": False,
                "is_gluten_free": False,
                "is_dairy_free": True,
                "is_keto_friendly": False,
                "is_nut_free": True
            },
            "health_score": 6.5
        }
    })

    result_id: Optional[str] = None
    scan_id: str = Field(..., description="Reference to the parent scan")
    user_id: str = Field(..., description="User who performed the scan")
    nutrition: NutritionSummary = Field(default_factory=NutritionSummary)
    allergens_detected: list[str] = Field(default_factory=list)
    dietary_suitability: DietarySuitability = Field(default_factory=DietarySuitability)
    health_score: float = Field(0.0, ge=0.0, le=10.0, description="Overall health score 0-10")
    created_at: Optional[str] = None
