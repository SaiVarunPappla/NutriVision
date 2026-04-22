"""
NutriVision - Recommendation Service Tests

Tests for generating personalized recommendations, warnings, and health scores.
"""

import pytest
from services.recommendation_service import generate_recommendations, calculate_health_score
from models.nutrition import NutritionSummary, NutrientDetail, DietarySuitability
from models.recommendation import RecommendationItem


def _make_nutrition(sugar=0, sodium=0, sat_fat=0, fiber=0, protein=0):
    """Helper to create nutrition summary for testing."""
    return NutritionSummary(
        total_calories=100,
        sugar=NutrientDetail(value=sugar/2, unit="g", daily_pct=sugar),
        sodium=NutrientDetail(value=sodium*10, unit="mg", daily_pct=sodium),
        saturated_fat=NutrientDetail(value=sat_fat/3, unit="g", daily_pct=sat_fat),
        fiber=NutrientDetail(value=fiber/4, unit="g", daily_pct=fiber),
        protein=NutrientDetail(value=protein/2, unit="g", daily_pct=protein),
    )


class TestRecommendationService:
    def test_high_sugar_warning(self):
        """Test that high sugar triggers a warning."""
        nutrition = _make_nutrition(sugar=60.0)
        suitability = DietarySuitability()
        
        recs = generate_recommendations(nutrition, [], suitability)
        
        warnings = [r for r in recs if r.type == "warning"]
        assert len(warnings) > 0
        assert "sugar" in warnings[0].title.lower()

    def test_allergen_alert(self):
        """Test that detected allergens trigger an alert."""
        nutrition = _make_nutrition()
        suitability = DietarySuitability()
        allergens = ["peanuts", "soy"]
        
        recs = generate_recommendations(nutrition, allergens, suitability)
        
        alerts = [r for r in recs if r.type == "allergen_alert"]
        assert len(alerts) > 0
        assert "peanuts" in alerts[0].message.lower()

    def test_personal_allergen_alert(self):
        """Test that user-specific allergens trigger a high-severity alert."""
        nutrition = _make_nutrition()
        suitability = DietarySuitability()
        allergens = ["peanuts"]
        user_allergies = ["peanuts"]
        
        recs = generate_recommendations(nutrition, allergens, suitability, user_allergies)
        
        alerts = [r for r in recs if r.type == "allergen_alert" and "Personal" in r.title]
        assert len(alerts) == 1
        assert alerts[0].severity == "high"

    def test_diet_mismatch(self):
        """Test that diet mismatch triggers a warning."""
        nutrition = _make_nutrition()
        suitability = DietarySuitability(is_vegan=False)
        user_prefs = ["vegan"]
        
        recs = generate_recommendations(nutrition, [], suitability, user_preferences=user_prefs)
        
        warnings = [r for r in recs if r.type == "warning"]
        assert len(warnings) > 0
        assert "vegan" in warnings[0].title.lower()

    def test_positive_suggestions(self):
        """Test that good nutrition triggers positive suggestions."""
        nutrition = _make_nutrition(fiber=25.0)  # High fiber
        suitability = DietarySuitability()
        
        recs = generate_recommendations(nutrition, [], suitability)
        
        suggestions = [r for r in recs if r.type == "suggestion"]
        assert len(suggestions) > 0
        assert "fiber" in suggestions[0].title.lower()

    def test_health_score_perfect(self):
        """Test health score for perfect food."""
        nutrition = _make_nutrition(sugar=10, sodium=10, sat_fat=10, fiber=20, protein=20)
        score = calculate_health_score(nutrition, [])
        
        # Base 7.0 + fiber bonus + protein bonus => should be > 8
        assert score > 8.0

    def test_health_score_poor(self):
        """Test health score for unhealthy food."""
        nutrition = _make_nutrition(sugar=80, sodium=70, sat_fat=60)
        score = calculate_health_score(nutrition, ["gluten", "soy"])
        
        # Penalties for sugar, sodium, sat_fat, and allergens
        assert score < 5.0
