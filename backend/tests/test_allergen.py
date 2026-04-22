"""
NutriVision - Allergen Detection Tests

Tests for allergen detection service.
Will be expanded in Phase 4 when the service is implemented.
"""

import pytest
from utils.constants import ALLERGEN_DATABASE


def test_allergen_database_loaded():
    """Test that the allergen database has all expected categories."""
    expected = [
        "milk", "eggs", "peanuts", "tree_nuts", "wheat",
        "gluten", "soy", "fish", "shellfish", "sesame",
    ]
    for allergen in expected:
        assert allergen in ALLERGEN_DATABASE, f"Missing allergen: {allergen}"


def test_allergen_keywords_not_empty():
    """Test that each allergen category has keywords."""
    for allergen, keywords in ALLERGEN_DATABASE.items():
        assert len(keywords) > 0, f"Empty keywords for: {allergen}"


def test_milk_allergen_keywords():
    """Test milk allergen keywords include common dairy terms."""
    dairy_terms = ["milk", "cream", "butter", "cheese", "whey", "casein"]
    for term in dairy_terms:
        assert term in ALLERGEN_DATABASE["milk"], f"Missing: {term}"
