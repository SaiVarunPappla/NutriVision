"""
NutriVision - Ingredient Parser Service Tests

Tests for the service layer that connects API routes to the NLP pipeline.
"""

import pytest
import asyncio
from services.ingredient_parser import parse_ingredients, parse_ingredients_with_metadata


def _run(coro):
    """Helper to run async functions in tests."""
    return asyncio.get_event_loop().run_until_complete(coro)


class TestParseIngredients:
    def test_simple_list(self):
        """Test parsing a simple comma-separated ingredient list."""
        result = _run(parse_ingredients("sugar, flour, butter, salt"))
        assert len(result) == 4
        assert result[0].normalized_name == "sugar"
        assert result[0].position == 1

    def test_returns_pydantic_models(self):
        """Test that results are proper IngredientBase objects."""
        result = _run(parse_ingredients("sugar, salt"))
        from models.ingredient import IngredientBase
        assert all(isinstance(r, IngredientBase) for r in result)

    def test_empty_input(self):
        """Test with empty text."""
        result = _run(parse_ingredients(""))
        assert result == []

    def test_none_input(self):
        """Test with None text."""
        result = _run(parse_ingredients(None))
        assert result == []

    def test_complex_label(self):
        """Test with realistic food label text."""
        label = (
            "INGREDIENTS: Enriched wheat flour, sugar, palm oil, "
            "cocoa powder (10%), soy lecithin, salt, baking soda."
        )
        result = _run(parse_ingredients(label))
        assert len(result) >= 5
        names = [r.normalized_name for r in result]
        assert "sugar" in names
        assert "salt" in names


class TestParseIngredientsWithMetadata:
    def test_returns_metadata(self):
        """Test that metadata includes count and allergen info."""
        result = _run(parse_ingredients_with_metadata(
            "INGREDIENTS: sugar, flour, salt, butter. Contains: wheat."
        ))
        assert "ingredients" in result
        assert "count" in result
        assert "allergen_warning" in result
        assert result["count"] >= 3

    def test_allergen_warning_detected(self):
        """Test allergen warning text extraction."""
        result = _run(parse_ingredients_with_metadata(
            "sugar, flour. Contains: wheat, soy."
        ))
        assert result["allergen_warning"] is not None
        assert "wheat" in result["allergen_warning"].lower()
