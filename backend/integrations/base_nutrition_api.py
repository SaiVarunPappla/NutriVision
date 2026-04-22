"""
NutriVision - Base Nutrition API Interface

Abstract base class that defines the contract for all nutrition API integrations.
This allows USDA and Edamam (or any future API) to be used interchangeably.

Design Pattern: Strategy Pattern
- USDANutritionAPI implements this for the primary working integration
- EdamamNutritionAPI implements this as an optional/pluggable fallback
"""

from abc import ABC, abstractmethod
from typing import Optional


class NutrientData:
    """Standardized nutrient data returned by any nutrition API."""

    def __init__(
        self,
        fdc_id: Optional[int] = None,
        name: str = "",
        calories: float = 0.0,
        protein: float = 0.0,
        carbohydrates: float = 0.0,
        fat: float = 0.0,
        fiber: float = 0.0,
        sugar: float = 0.0,
        sodium: float = 0.0,
        saturated_fat: float = 0.0,
        cholesterol: float = 0.0,
        serving_size: float = 100.0,
        serving_unit: str = "g",
        source: str = "unknown",
        confidence: float = 0.0, # New field
        matched_name: str = "", # New field
        matched_type: str = "no_match", # New field: 'branded', 'generic_ingredient', 'estimated_ingredient', 'no_match'
    ):
        self.fdc_id = fdc_id
        self.name = name
        self.calories = calories
        self.protein = protein
        self.carbohydrates = carbohydrates
        self.fat = fat
        self.fiber = fiber
        self.sugar = sugar
        self.sodium = sodium
        self.saturated_fat = saturated_fat
        self.cholesterol = cholesterol
        self.serving_size = serving_size
        self.serving_unit = serving_unit
        self.source = source
        self.confidence = confidence # New
        self.matched_name = matched_name # New
        self.matched_type = matched_type # New

    def to_dict(self) -> dict:
        """Convert to dictionary for Firestore storage."""
        return {
            "fdc_id": self.fdc_id,
            "name": self.name,
            "calories": self.calories,
            "protein": self.protein,
            "carbohydrates": self.carbohydrates,
            "fat": self.fat,
            "fiber": self.fiber,
            "sugar": self.sugar,
            "sodium": self.sodium,
            "saturated_fat": self.saturated_fat,
            "cholesterol": self.cholesterol,
            "serving_size": self.serving_size,
            "serving_unit": self.serving_unit,
            "source": self.source,
            "confidence": self.confidence, # New
            "matched_name": self.matched_name, # New
            "matched_type": self.matched_type, # New
        }


class BaseNutritionAPI(ABC):
    """
    Abstract base class for nutrition API integrations.

    Any nutrition data provider must implement these methods:
    - search_food(): Find a food item by name
    - get_food_details(): Get full nutrition for a specific food ID
    - is_available(): Check if the API is configured and reachable
    """

    @abstractmethod
    async def search_food(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Search for food items matching a query string.

        Args:
            query: Food name to search (e.g., "wheat flour")
            max_results: Maximum number of results to return

        Returns:
            List of matching food items with basic info
        """
        pass

    @abstractmethod
    async def get_food_details(self, food_id: int) -> Optional[NutrientData]:
        """
        Get detailed nutrition data for a specific food item.

        Args:
            food_id: The food item's unique identifier (e.g., USDA FDC ID)

        Returns:
            NutrientData object with full nutritional breakdown, or None
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if this API integration is configured and reachable.

        Returns:
            True if the API can be used, False otherwise
        """
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this data source (e.g., 'USDA', 'Edamam')."""
        pass
