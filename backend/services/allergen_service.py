"""
NutriVision - Allergen Detection Service

Detects common food allergens from parsed ingredient lists using
rule-based keyword matching against the Big 14 allergen database.

Supports:
- Standard allergen detection (Big 14)
- User-specific allergen alerting (personalized)
- Confidence scoring based on match type
"""

from models.ingredient import IngredientBase
from utils.constants import ALLERGEN_DATABASE


def detect_allergens(
    ingredients: list[IngredientBase],
    user_allergies: list[str] = None,
) -> dict:
    """
    Detect allergens present in the ingredient list.

    Args:
        ingredients: List of parsed ingredients
        user_allergies: User's known allergies for personalized alerts

    Returns:
        Dict with:
        - 'detected': list of allergen names found
        - 'details': list of dicts with allergen, trigger ingredient, match type
        - 'user_alerts': list of allergens that match user's known allergies
        - 'count': total number of allergens detected
    """
    if not ingredients:
        return {"detected": [], "details": [], "user_alerts": [], "count": 0}

    detected = set()
    details = []

    for ingredient in ingredients:
        name = ingredient.normalized_name.lower()
        matches = _match_allergens(name)

        for allergen, keyword, match_type in matches:
            if allergen not in detected:
                detected.add(allergen)
                details.append({
                    "allergen": allergen,
                    "trigger_ingredient": ingredient.name,
                    "matched_keyword": keyword,
                    "match_type": match_type,
                })

    # Check user-specific allergen alerts
    user_alerts = []
    if user_allergies:
        normalized_user = [a.lower().replace("-", "_").replace(" ", "_") for a in user_allergies]
        for allergen in detected:
            if allergen in normalized_user or allergen.replace("_", " ") in [a.lower() for a in user_allergies]:
                user_alerts.append(allergen)

    return {
        "detected": sorted(detected),
        "details": details,
        "user_alerts": sorted(user_alerts),
        "count": len(detected),
    }


def _match_allergens(ingredient_name: str) -> list[tuple[str, str, str]]:
    """
    Match an ingredient name against the allergen database.

    Returns list of (allergen_category, matched_keyword, match_type) tuples.
    match_type is either 'exact' or 'partial'.
    """
    matches = []
    name_lower = ingredient_name.lower().strip()

    for allergen_category, keywords in ALLERGEN_DATABASE.items():
        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Exact match: ingredient IS the keyword
            if name_lower == keyword_lower:
                matches.append((allergen_category, keyword, "exact"))
                break

            # Partial match: keyword appears within ingredient name
            if keyword_lower in name_lower:
                matches.append((allergen_category, keyword, "partial"))
                break

            # Reverse partial: ingredient name appears in keyword
            if len(name_lower) > 3 and name_lower in keyword_lower:
                matches.append((allergen_category, keyword, "partial"))
                break

    return matches


def get_allergen_names_only(
    ingredients: list[IngredientBase],
    user_allergies: list[str] = None,
) -> list[str]:
    """
    Simplified version that returns just allergen names.
    Used by the scan route for the response model.
    """
    result = detect_allergens(ingredients, user_allergies)
    return result["detected"]
