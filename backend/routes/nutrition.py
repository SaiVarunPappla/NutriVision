"""
NutriVision - Nutrition Routes

API endpoints for retrieving nutrition analysis results.
"""

from fastapi import APIRouter, HTTPException
from models.nutrition import NutritionResult

router = APIRouter()


@router.get(
    "/nutrition/{scan_id}",
    response_model=NutritionResult,
    summary="Get Nutrition Results",
    description="Retrieve detailed nutrition analysis for a completed scan."
)
async def get_nutrition(scan_id: str):
    """
    Get the full nutrition breakdown for a specific scan.

    Returns:
    - Calorie count
    - Macronutrient breakdown (protein, carbs, fat)
    - Micronutrient details
    - Allergen list
    - Dietary suitability flags
    - Health score
    """
    # TODO: Implement Firestore lookup in Phase 4
    raise HTTPException(
        status_code=404,
        detail=f"Nutrition results for scan '{scan_id}' not found. Implementation pending Phase 4."
    )
