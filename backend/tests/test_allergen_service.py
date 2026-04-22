"""
NutriVision - Allergen Detection Service Tests

Tests for rule-based allergen matching and personalized alerting.
"""

import pytest
from services.allergen_service import detect_allergens, get_allergen_names_only
from models.ingredient import IngredientBase


class TestAllergenService:
    def test_exact_match(self):
        """Test exact keyword matching."""
        ingredients = [IngredientBase(name="milk", normalized_name="milk", position=1)]
        result = detect_allergens(ingredients)
        
        assert "milk" in result["detected"]
        assert result["count"] == 1
        assert result["details"][0]["match_type"] == "exact"

    def test_partial_match(self):
        """Test partial keyword matching."""
        ingredients = [IngredientBase(name="skimmed milk", normalized_name="skim milk", position=1)]
        result = detect_allergens(ingredients)
        
        assert "milk" in result["detected"]
        assert result["details"][0]["match_type"] == "partial"

    def test_multiple_allergens(self):
        """Test detecting multiple allergens from complex ingredients."""
        ingredients = [
            IngredientBase(name="soy sauce", normalized_name="soy sauce", position=1),
            IngredientBase(name="wheat flour", normalized_name="wheat flour", position=2),
        ]
        result = detect_allergens(ingredients)
        
        assert "soy" in result["detected"]
        assert "wheat" in result["detected"]
        assert "gluten" in result["detected"]
        assert result["count"] == 3

    def test_user_allergies_matched(self):
        """Test that user-specific allergies trigger alerts."""
        ingredients = [IngredientBase(name="peanuts", normalized_name="peanuts", position=1)]
        user_allergies = ["peanuts", "shellfish"]
        
        result = detect_allergens(ingredients, user_allergies)
        
        assert "peanuts" in result["detected"]
        assert "peanuts" in result["user_alerts"]

    def test_user_allergies_normalized(self):
        """Test that user allergies are matched regardless of formatting."""
        ingredients = [IngredientBase(name="tree nuts", normalized_name="almond", position=1)]
        # User entered "tree-nuts"
        user_allergies = ["tree-nuts"]
        
        result = detect_allergens(ingredients, user_allergies)
        
        assert "tree_nuts" in result["detected"]
        assert "tree_nuts" in result["user_alerts"]

    def test_no_allergens(self):
        """Test behavior when no allergens are present."""
        ingredients = [IngredientBase(name="water", normalized_name="water", position=1)]
        result = detect_allergens(ingredients)
        
        assert result["count"] == 0
        assert not result["detected"]

    def test_get_allergen_names_only(self):
        """Test the simplified names-only helper."""
        ingredients = [IngredientBase(name="milk powder", normalized_name="milk powder", position=1)]
        names = get_allergen_names_only(ingredients)
        
        assert names == ["milk"]
