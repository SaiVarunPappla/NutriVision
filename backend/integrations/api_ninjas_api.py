"""
NutriVision - API-Ninjas Nutrition API Integration (Fallback)

Provides nutrition data using the API-Ninjas service.
This is intended as a fallback if USDA and Edamam fail or are unavailable.

API Documentation: https://api-ninjas.com/api/nutrition
API Key Signup:    https://api-ninjas.com/ (free tier available)
"""

import httpx
from typing import Optional
from integrations.base_nutrition_api import BaseNutritionAPI, NutrientData
from config import settings
import asyncio

REQUEST_TIMEOUT = 10.0 # Timeout for API requests

class ApiNinjasNutritionAPI(BaseNutritionAPI):
    """
    API-Ninjas Nutrition API client.
    Used as a fallback data source.
    """

    def __init__(self):
        self.api_key = settings.api_ninjas_api_key
        self.base_url = settings.api_ninjas_base_url

    async def search_food(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Search API-Ninjas for food items.
        """
        if not await self.is_available():
            return []

        url = f"{self.base_url}/nutrition"
        params = {"query": query}
        headers = {"X-Api-Key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()

            # API-Ninjas returns a list of foods directly if the structure is correct
            # Log the data to debug the structure
            # print(f"[API-Ninjas] Data for '{query}': {data}")

            # Correct logic: API-Ninjas returns a list of dictionaries directly if successful
            if isinstance(data, list):
                results = []
                for item in data[:max_results]:
                    item_name = item.get("name", "")
                    confidence = 0.7 if query.lower() in item_name.lower() else 0.5 # Simple confidence based on substring match
                    matched_type = "generic_ingredient"
                    
                    results.append({
                        "food_id": item_name,
                        "description": item_name,
                        "source": "API-Ninjas",
                        "confidence": confidence,
                        "matched_type": matched_type,
                    })
                return results
            else:
                return []

        except Exception as e:
            print(f"[API-Ninjas] Search error for '{query}': {e}")
            return []

    async def get_food_details(self, food_id: str) -> Optional[NutrientData]:
        """
        Get nutrition details for a specific food item from API-Ninjas.
        """
        if not await self.is_available() or not food_id:
            return None

        url = f"{self.base_url}/nutrition"
        params = {"query": food_id}
        headers = {"X-Api-Key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()

            # API-Ninjas returns a list of foods directly
            if isinstance(data, list) and len(data) > 0:
                return self._parse_nutrition_data(data[0], query_name=food_id)
            else:
                return None

        except Exception as e:
            print(f"[API-Ninjas] Detail error for food '{food_id}': {e}")
            return None

    def _parse_nutrition_data(self, nutrition_data: dict, query_name: str) -> NutrientData:
        """Parse API-Ninjas nutrition data into our standardized NutrientData format."""
        matched_name = nutrition_data.get("name", query_name)
        confidence = 0.8 # Assume good confidence for direct detail lookup
        matched_type = "generic_ingredient"

        return NutrientData(
            name=query_name, # This will be overwritten by original query in service layer
            matched_name=matched_name,
            calories=float(nutrition_data.get("calories", 0.0)),
            protein=float(nutrition_data.get("protein_g", 0.0)),
            carbohydrates=float(nutrition_data.get("carbohydrates_total_g", 0.0)),
            fat=float(nutrition_data.get("fat_total_g", 0.0)),
            fiber=float(nutrition_data.get("fiber_g", 0.0)),
            sugar=float(nutrition_data.get("sugar_g", 0.0)),
            sodium=float(nutrition_data.get("sodium_mg", 0.0)),
            saturated_fat=float(nutrition_data.get("fat_saturated_g", 0.0)),
            cholesterol=float(nutrition_data.get("cholesterol_mg", 0.0)),
            serving_size=float(nutrition_data.get("serving_size_g", 100.0)),
            serving_unit="g",
            source="API-Ninjas",
            confidence=confidence,
            matched_type=matched_type,
        )

    async def is_available(self) -> bool:
        return bool(self.api_key)

    @property
    def source_name(self) -> str:
        return "API-Ninjas"
