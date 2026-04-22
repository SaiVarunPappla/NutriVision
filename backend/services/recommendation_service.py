"""
NutriVision - Recommendation Service

Generates personalized health recommendations based on:
- Nutrition analysis results (high sodium, sugar warnings, etc.)
- Detected allergens (user-specific alerts)
- Dietary suitability flags
- User dietary preferences

Also calculates the overall health score (0-10).
"""

from models.recommendation import RecommendationItem
from models.nutrition import NutritionSummary, DietarySuitability
from utils.constants import HEALTH_SCORE_WEIGHTS, DAILY_VALUES


def generate_recommendations(
    nutrition: NutritionSummary,
    allergens: list[str],
    dietary_suitability: DietarySuitability,
    user_allergies: list[str] = None,
    user_preferences: list[str] = None,
) -> list[RecommendationItem]:
    """
    Generate personalized recommendations based on analysis results.

    Returns a list of warnings, allergen alerts, and suggestions.
    """
    recommendations = []

    # 1. Nutritional warnings
    recommendations.extend(_nutrition_warnings(nutrition))

    # 2. Allergen alerts
    recommendations.extend(_allergen_alerts(allergens, user_allergies))

    # 3. Dietary mismatch alerts
    recommendations.extend(_diet_mismatch_alerts(dietary_suitability, user_preferences))

    # 4. Positive suggestions
    recommendations.extend(_positive_suggestions(nutrition, dietary_suitability))

    return recommendations


def calculate_health_score(
    nutrition: NutritionSummary,
    allergens: list[str],
) -> float:
    """
    Calculate an overall health score (0-10) for the analyzed food.

    Higher is healthier. Factors:
    - Penalize high sugar, sodium, saturated fat
    - Bonus for fiber and protein
    - Penalize per allergen detected
    """
    w = HEALTH_SCORE_WEIGHTS
    score = w["base_score"]  # Start at 7.0

    # Sugar penalty: if sugar > 50% daily value
    sugar_pct = nutrition.sugar.daily_pct
    if sugar_pct > 50:
        excess = (sugar_pct - 50) / 25
        score += w["high_sugar_penalty"] * excess

    # Sodium penalty
    sodium_pct = nutrition.sodium.daily_pct
    if sodium_pct > 50:
        excess = (sodium_pct - 50) / 25
        score += w["high_sodium_penalty"] * excess

    # Saturated fat penalty
    sat_fat_pct = nutrition.saturated_fat.daily_pct
    if sat_fat_pct > 50:
        excess = (sat_fat_pct - 50) / 25
        score += w["high_sat_fat_penalty"] * excess

    # Fiber bonus
    fiber_pct = nutrition.fiber.daily_pct
    fiber_bonus = (fiber_pct / 10) * w["fiber_bonus"]
    score += min(fiber_bonus, 1.5)  # cap bonus

    # Protein bonus
    protein_pct = nutrition.protein.daily_pct
    protein_bonus = (protein_pct / 10) * w["protein_bonus"]
    score += min(protein_bonus, 1.0)  # cap bonus

    # Allergen penalty
    score += len(allergens) * w["allergen_penalty"]

    # Clamp to 0-10 range
    return round(max(0.0, min(10.0, score)), 1)


# ============================================================
# Internal recommendation generators
# ============================================================

def _nutrition_warnings(nutrition: NutritionSummary) -> list[RecommendationItem]:
    """Generate warnings for nutritional concerns."""
    warnings = []

    # High sugar warning
    if nutrition.sugar.daily_pct > 40:
        severity = "high" if nutrition.sugar.daily_pct > 75 else "medium"
        warnings.append(RecommendationItem(
            type="warning",
            title="High Sugar Content",
            message=f"This product contains {nutrition.sugar.value}g of sugar "
                    f"({nutrition.sugar.daily_pct}% of daily value). "
                    f"Consider lower-sugar alternatives.",
            severity=severity,
        ))

    # High sodium warning
    if nutrition.sodium.daily_pct > 30:
        severity = "high" if nutrition.sodium.daily_pct > 60 else "medium"
        warnings.append(RecommendationItem(
            type="warning",
            title="High Sodium Content",
            message=f"This product contains {nutrition.sodium.value}mg of sodium "
                    f"({nutrition.sodium.daily_pct}% of daily value). "
                    f"High sodium intake may affect blood pressure.",
            severity=severity,
        ))

    # High saturated fat warning
    if nutrition.saturated_fat.daily_pct > 35:
        severity = "high" if nutrition.saturated_fat.daily_pct > 70 else "medium"
        warnings.append(RecommendationItem(
            type="warning",
            title="High Saturated Fat",
            message=f"This product contains {nutrition.saturated_fat.value}g of saturated fat "
                    f"({nutrition.saturated_fat.daily_pct}% of daily value). "
                    f"Consider alternatives with unsaturated fats.",
            severity=severity,
        ))

    # High cholesterol warning
    if nutrition.cholesterol.daily_pct > 50:
        warnings.append(RecommendationItem(
            type="warning",
            title="High Cholesterol",
            message=f"This product contains {nutrition.cholesterol.value}mg of cholesterol "
                    f"({nutrition.cholesterol.daily_pct}% of daily value).",
            severity="medium",
        ))

    # High calorie warning
    if nutrition.total_calories > 500:
        warnings.append(RecommendationItem(
            type="warning",
            title="High Calorie Content",
            message=f"This product contains approximately {nutrition.total_calories} calories "
                    f"per serving. Plan your daily intake accordingly.",
            severity="medium",
        ))

    return warnings


def _allergen_alerts(
    allergens: list[str],
    user_allergies: list[str] = None,
) -> list[RecommendationItem]:
    """Generate allergen alert recommendations."""
    alerts = []

    if not allergens:
        return alerts

    # General allergen notice
    allergen_str = ", ".join(allergens)
    alerts.append(RecommendationItem(
        type="allergen_alert",
        title=f"Allergens Detected ({len(allergens)})",
        message=f"This product may contain: {allergen_str}. "
                f"Check the label carefully if you have food allergies.",
        severity="high",
    ))

    # User-specific allergen alerts
    if user_allergies:
        user_set = {a.lower().replace("-", "_").replace(" ", "_") for a in user_allergies}
        personal_matches = [a for a in allergens if a in user_set]

        if personal_matches:
            match_str = ", ".join(personal_matches)
            alerts.append(RecommendationItem(
                type="allergen_alert",
                title="⚠️ Personal Allergen Alert",
                message=f"WARNING: This product contains {match_str}, "
                        f"which is in your allergen profile. Avoid consumption!",
                severity="high",
            ))

    return alerts


def _diet_mismatch_alerts(
    suitability: DietarySuitability,
    user_preferences: list[str] = None,
) -> list[RecommendationItem]:
    """Generate alerts when food doesn't match user's dietary preferences."""
    alerts = []

    if not user_preferences:
        return alerts

    pref_lower = [p.lower().replace("-", "_").replace(" ", "_") for p in user_preferences]

    diet_checks = {
        "vegetarian": suitability.is_vegetarian,
        "vegan": suitability.is_vegan,
        "gluten_free": suitability.is_gluten_free,
        "dairy_free": suitability.is_dairy_free,
        "keto": suitability.is_keto_friendly,
        "keto_friendly": suitability.is_keto_friendly,
        "nut_free": suitability.is_nut_free,
    }

    for pref in pref_lower:
        if pref in diet_checks and not diet_checks[pref]:
            readable = pref.replace("_", " ").title()
            alerts.append(RecommendationItem(
                type="warning",
                title=f"Not {readable}",
                message=f"This product does not meet your {readable} dietary preference. "
                        f"Some ingredients are not compatible with this diet.",
                severity="medium",
            ))

    return alerts


def _positive_suggestions(
    nutrition: NutritionSummary,
    suitability: DietarySuitability,
) -> list[RecommendationItem]:
    """Generate positive suggestions and tips."""
    suggestions = []

    # Good fiber content
    if nutrition.fiber.daily_pct > 15:
        suggestions.append(RecommendationItem(
            type="suggestion",
            title="Good Fiber Source",
            message=f"This product provides {nutrition.fiber.value}g of fiber "
                    f"({nutrition.fiber.daily_pct}% of daily value). "
                    f"Fiber supports digestive health.",
            severity="low",
        ))

    # Good protein content
    if nutrition.protein.daily_pct > 20:
        suggestions.append(RecommendationItem(
            type="suggestion",
            title="Good Protein Source",
            message=f"This product provides {nutrition.protein.value}g of protein "
                    f"({nutrition.protein.daily_pct}% of daily value).",
            severity="low",
        ))

    # Low calorie product
    if 0 < nutrition.total_calories < 100:
        suggestions.append(RecommendationItem(
            type="info",
            title="Low Calorie",
            message=f"This product is relatively low in calories ({nutrition.total_calories} kcal). "
                    f"Good choice for calorie-conscious meals.",
            severity="low",
        ))

    # Vegan-friendly positive note
    if suitability.is_vegan:
        suggestions.append(RecommendationItem(
            type="info",
            title="Vegan Friendly",
            message="This product appears to be suitable for a vegan diet.",
            severity="low",
        ))

    return suggestions
