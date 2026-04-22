"""
NutriVision - Dietary Suitability Tests

Tests for dietary suitability detection service.
Will be expanded in Phase 4 when the service is implemented.
"""

import pytest
from utils.constants import (
    NON_VEGETARIAN_INGREDIENTS,
    NON_VEGAN_INGREDIENTS,
    HIGH_CARB_INGREDIENTS,
    DAILY_VALUES,
)


def test_non_veg_ingredients_loaded():
    """Test non-vegetarian ingredient list is populated."""
    assert len(NON_VEGETARIAN_INGREDIENTS) > 0
    assert "meat" in NON_VEGETARIAN_INGREDIENTS
    assert "chicken" in NON_VEGETARIAN_INGREDIENTS


def test_non_vegan_includes_non_veg():
    """Test that non-vegan list includes all non-vegetarian items."""
    for item in NON_VEGETARIAN_INGREDIENTS:
        assert item in NON_VEGAN_INGREDIENTS, f"Missing in vegan list: {item}"


def test_non_vegan_includes_dairy_eggs():
    """Test non-vegan list includes dairy and egg products."""
    assert "milk" in NON_VEGAN_INGREDIENTS
    assert "egg" in NON_VEGAN_INGREDIENTS
    assert "honey" in NON_VEGAN_INGREDIENTS
    assert "butter" in NON_VEGAN_INGREDIENTS


def test_high_carb_ingredients():
    """Test high-carb list includes expected items."""
    assert "sugar" in HIGH_CARB_INGREDIENTS
    assert "flour" in HIGH_CARB_INGREDIENTS
    assert "rice" in HIGH_CARB_INGREDIENTS


def test_daily_values_complete():
    """Test daily value reference data is complete."""
    required = ["calories", "protein", "carbohydrates", "fat", "fiber", "sodium"]
    for nutrient in required:
        assert nutrient in DAILY_VALUES, f"Missing DV: {nutrient}"
        assert DAILY_VALUES[nutrient] > 0, f"Invalid DV for: {nutrient}"
