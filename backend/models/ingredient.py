"""
NutriVision - Ingredient Models

Pydantic models for parsed ingredient data.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class IngredientBase(BaseModel):
    """Base ingredient data extracted from OCR or text input."""
    name: str = Field(..., description="Raw ingredient name as extracted")
    normalized_name: str = Field(..., description="Cleaned/normalized ingredient name")
    position: int = Field(..., description="Position in the ingredient list (1-based)")


class IngredientWithNutrition(IngredientBase):
    """Ingredient enriched with USDA nutrition data."""
    usda_fdc_id: Optional[int] = Field(None, description="USDA FoodData Central ID")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Match confidence score")
    calories: float = Field(0.0, description="Calories per 100g")
    protein: float = Field(0.0, description="Protein in grams per 100g")
    carbohydrates: float = Field(0.0, description="Carbohydrates in grams per 100g")
    fat: float = Field(0.0, description="Fat in grams per 100g")


class IngredientCreate(BaseModel):
    """Data needed to store an ingredient in Firestore."""
    name: str
    normalized_name: str
    usda_fdc_id: Optional[int] = None
    confidence: float = 0.0
    position: int = 1


class IngredientResponse(IngredientBase):
    """Ingredient data returned in API responses."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "ingredient_id": "abc123",
            "name": "enriched wheat flour",
            "normalized_name": "wheat flour",
            "usda_fdc_id": 169761,
            "match_confidence": 0.92, # Renamed from 'confidence'
            "nutrition_source": "USDA FoodData Central",
            "matched_name": "Wheat flour, bleached, enriched",
            "matched_type": "generic_ingredient",
            "position": 1
        }
    })

    ingredient_id: Optional[str] = None
    usda_fdc_id: Optional[int] = None
    # Renamed 'confidence' to 'match_confidence' to distinguish from OCR confidence
    match_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score for the nutrition match of this ingredient (0.0 to 1.0)")
    nutrition_source: Optional[str] = Field(None, description="Source API for this ingredient's nutrition (e.g., 'USDA', 'Edamam')")
    matched_name: Optional[str] = Field(None, description="Exact name of the ingredient as matched in the nutrition database")
    matched_type: Optional[str] = Field(None, description="Type of match: 'branded', 'generic_ingredient', 'estimated_ingredient', 'no_match'")

