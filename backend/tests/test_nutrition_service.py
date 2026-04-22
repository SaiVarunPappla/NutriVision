"""
NutriVision - Nutrition Service Tests

Tests for nutrition lookup, API response parsing, and calculation
of total nutrients and daily value percentages.
"""

import pytest
import asyncio
from services.nutrition_service import lookup_nutrition, _get_demo_nutrition, _aggregate_nutrition
from models.ingredient import IngredientBase
from utils.constants import USDA_NUTRIENT_MAP


def _run(coro):
    """Helper to run async functions in tests."""
    return asyncio.get_event_loop().run_until_complete(coro)


class TestNutritionService:
    def test_demo_nutrition_lookup_exact(self):
        """Test getting demo data with exact match."""
        data = _get_demo_nutrition("wheat flour")
        assert data is not None
        assert data.name == "wheat flour"
        assert data.source == "demo"
        assert data.calories > 0

    def test_demo_nutrition_lookup_partial(self):
        """Test getting demo data with partial match."""
        data = _get_demo_nutrition("enriched wheat flour")
        assert data is not None
        assert "wheat flour" in data.name
        assert data.source == "demo"

    def test_demo_nutrition_lookup_unknown(self):
        """Test getting generic fallback data for unknown ingredient."""
        data = _get_demo_nutrition("unicorn dust")
        assert data is not None
        assert data.name == "unicorn dust"
        assert data.source == "demo_estimate"
        assert data.calories == 50

    def test_aggregate_empty_list(self):
        """Test aggregation with empty input."""
        summary = _aggregate_nutrition([])
        assert summary.total_calories == 0.0

    def test_aggregate_nutrition(self):
        """Test aggregation calculations."""
        per_ingredient = [
            {"nutrition": _get_demo_nutrition("sugar")},
            {"nutrition": _get_demo_nutrition("salt")},
        ]
        
        summary = _aggregate_nutrition(per_ingredient)
        
        # Should be avg of sugar (387) and salt (0)
        expected_calories = round((387 + 0) / 2, 1)
        assert summary.total_calories == expected_calories
        
        # Sugar has 100g sugar, salt has 0. Avg = 50.
        assert summary.sugar.value == 50.0
        
        # Daily values should be computed
        assert summary.sugar.daily_pct > 0

    def test_lookup_nutrition_demo_mode(self):
        """Test the full lookup function in demo mode."""
        ingredients = [
            IngredientBase(name="sugar", normalized_name="sugar", position=1),
            IngredientBase(name="salt", normalized_name="salt", position=2),
        ]
        
        # use_api=False forces demo mode
        summary, per_ingredient = _run(lookup_nutrition(ingredients, use_api=False))
        
        assert len(per_ingredient) == 2
        assert per_ingredient[0]["source"] == "demo"
        assert per_ingredient[1]["source"] == "demo"
        assert summary.total_calories > 0
