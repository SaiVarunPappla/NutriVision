"""
NutriVision - Dietary Suitability Service

Evaluates whether a food product is suitable for various diets
based on its ingredient list. Uses rule-based classification.

Checks 6 diet types:
- Vegetarian: no meat, poultry, fish, shellfish
- Vegan: no animal products at all
- Gluten-free: no wheat, barley, rye, oats, malt
- Dairy-free: no milk, cream, butter, cheese, whey, casein, lactose
- Keto-friendly: no high-carb ingredients
- Nut-free: no peanuts, tree nuts
"""

from models.nutrition import DietarySuitability
from models.ingredient import IngredientBase
from utils.constants import (
    NON_VEGETARIAN_INGREDIENTS,
    NON_VEGAN_INGREDIENTS,
    HIGH_CARB_INGREDIENTS,
    ALLERGEN_DATABASE,
)


def check_dietary_suitability(ingredients: list[IngredientBase]) -> DietarySuitability:
    """
    Check dietary suitability based on ingredient analysis.

    Args:
        ingredients: List of parsed ingredients

    Returns:
        DietarySuitability with flags for each diet type
    """
    if not ingredients:
        return DietarySuitability(
            is_vegetarian=True, is_vegan=True, is_gluten_free=True,
            is_dairy_free=True, is_keto_friendly=True, is_nut_free=True,
        )

    # Collect all normalized ingredient names
    names = [ing.normalized_name.lower() for ing in ingredients]

    return DietarySuitability(
        is_vegetarian=_check_vegetarian(names),
        is_vegan=_check_vegan(names),
        is_gluten_free=_check_gluten_free(names),
        is_dairy_free=_check_dairy_free(names),
        is_keto_friendly=_check_keto_friendly(names),
        is_nut_free=_check_nut_free(names),
    )


def _check_vegetarian(names: list[str]) -> bool:
    """Check if all ingredients are vegetarian."""
    for name in names:
        for non_veg in NON_VEGETARIAN_INGREDIENTS:
            if non_veg in name or name in non_veg:
                return False
    return True


def _check_vegan(names: list[str]) -> bool:
    """Check if all ingredients are vegan (no animal products)."""
    for name in names:
        for non_vegan in NON_VEGAN_INGREDIENTS:
            if non_vegan in name or name in non_vegan:
                return False
    return True


def _check_gluten_free(names: list[str]) -> bool:
    """Check if no gluten-containing ingredients are present."""
    gluten_keywords = ALLERGEN_DATABASE.get("gluten", [])
    for name in names:
        for keyword in gluten_keywords:
            if keyword.lower() in name or name in keyword.lower():
                return False
    return True


def _check_dairy_free(names: list[str]) -> bool:
    """Check if no dairy ingredients are present."""
    dairy_keywords = ALLERGEN_DATABASE.get("milk", [])
    for name in names:
        for keyword in dairy_keywords:
            if keyword.lower() in name or name in keyword.lower():
                return False
    return True


def _check_keto_friendly(names: list[str]) -> bool:
    """Check if no high-carb ingredients are present."""
    for name in names:
        for high_carb in HIGH_CARB_INGREDIENTS:
            if high_carb in name or name in high_carb:
                return False
    return True


def _check_nut_free(names: list[str]) -> bool:
    """Check if no nut ingredients are present."""
    nut_keywords = (
        ALLERGEN_DATABASE.get("peanuts", []) +
        ALLERGEN_DATABASE.get("tree_nuts", [])
    )
    for name in names:
        for keyword in nut_keywords:
            if keyword.lower() in name or name in keyword.lower():
                return False
    return True


def get_diet_summary(suitability: DietarySuitability) -> list[str]:
    """
    Get a human-readable list of suitable diets.
    Returns: e.g. ["Vegetarian", "Dairy-free", "Nut-free"]
    """
    diets = []
    if suitability.is_vegetarian:
        diets.append("Vegetarian")
    if suitability.is_vegan:
        diets.append("Vegan")
    if suitability.is_gluten_free:
        diets.append("Gluten-free")
    if suitability.is_dairy_free:
        diets.append("Dairy-free")
    if suitability.is_keto_friendly:
        diets.append("Keto-friendly")
    if suitability.is_nut_free:
        diets.append("Nut-free")
    return diets
