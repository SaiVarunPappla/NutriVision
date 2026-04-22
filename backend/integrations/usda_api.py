"""
NutriVision - USDA FoodData Central API Integration

PRIMARY nutrition data source (free, no paid tier required).

API Documentation: https://fdc.nal.usda.gov/api-guide.html
API Key Signup:    https://fdc.nal.usda.gov/api-key-signup.html

Endpoints used:
- POST /v1/foods/search  → Search foods by name
- GET  /v1/food/{fdcId}  → Get detailed nutrition for a food item
"""

import httpx
from typing import Optional
from integrations.base_nutrition_api import BaseNutritionAPI, NutrientData
from config import settings
from utils.constants import USDA_NUTRIENT_MAP

# Timeout for HTTP requests (seconds)
REQUEST_TIMEOUT = 10.0


class USDANutritionAPI(BaseNutritionAPI):
    """
    USDA FoodData Central API client.
    """

    def __init__(self):
        self.api_key = settings.usda_api_key
        self.base_url = settings.usda_base_url

    async def search_food(self, query: str, max_results: int = 5, is_branded_search: bool = False) -> list[dict]:
        """
        Search USDA database for food items matching the query.
        """
        url = f"{self.base_url}/foods/search"
        params = {"api_key": self.api_key}
        
        # Changed: Ensure data types are correct. "Foundation" is often most reliable.
        data_types = ["Foundation", "SR Legacy", "Survey (FNDDS)", "Branded"]
        
        payload = {
            "query": query,
            "pageSize": max_results,
            "dataType": data_types,
        }

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(url, params=params, json=payload)
                response.raise_for_status()
                data = response.json()

            foods = data.get("foods", [])
            results = []
            for food in foods[:max_results]:
                results.append({
                    "fdc_id": food.get("fdcId"),
                    "description": food.get("description", ""),
                    "data_type": food.get("dataType", ""),
                    "brand_owner": food.get("brandOwner", ""),
                    "score": food.get("score", 0),
                })
            return results

        except Exception as e:
            print(f"[USDA] Search error for '{query}': {e}")
            return []

    async def get_food_details(self, food_id: int, data_type: str = "unknown", score: float = 0.0) -> Optional[NutrientData]:
        """
        Get full nutritional data for a specific FDC food ID.
        Accepts data_type and score from search for better confidence calculation.
        """
        url = f"{self.base_url}/food/{food_id}"
        params = {
            "api_key": self.api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            # Pass data_type and score along to the parser
            return self._parse_nutrients(data, data_type=data_type, score=score)

        except Exception as e:
            print(f"[USDA] Detail error for ID {food_id}: {e}")
            return None

    async def search_and_get_nutrition(self, ingredient_name: str, is_branded_search: bool = False) -> Optional[NutrientData]:
        """
        Convenience method: search for an ingredient/product and get its nutrition.
        """
        results = await self.search_food(ingredient_name, max_results=1, is_branded_search=is_branded_search)
        if not results:
            return None

        fdc_id = results[0]["fdc_id"]
        # Pass data_type and score from search results to get_food_details for better nutrient data parsing
        data_type = results[0].get("data_type", "unknown")
        score = results[0].get("score", 0.0)
        nutrient_data = await self.get_food_details(fdc_id, data_type=data_type, score=score)

        if nutrient_data:
            # The 'name' property of NutrientData should be the original query for aggregation purposes.
            # 'matched_name' will hold the exact name found in the database.
            nutrient_data.name = ingredient_name
            nutrient_data.fdc_id = fdc_id

        return nutrient_data

    def _parse_nutrients(self, food_data: dict, data_type: str = "unknown", score: float = 0.0) -> NutrientData:
        """Parse USDA API response into our standardized NutrientData format, including confidence and type."""
        nutrients_list = food_data.get("foodNutrients", [])

        nutrient_values = {}
        for item in nutrients_list:
            nutrient = item.get("nutrient", {})
            number = nutrient.get("number")
            amount = item.get("amount")

            if number:
                try:
                    nutrient_values[int(float(number))] = float(amount) if amount else 0.0
                except (ValueError, TypeError):
                    pass

        # Determine confidence and matched_type based on USDA data_type and score
        confidence = 0.0
        matched_type = "no_match"

        if data_type == "Branded":
            confidence = min(1.0, max(0.0, score / 1000.0)) # USDA scores can be high, normalize to 0-1
            matched_type = "branded_product"
        elif data_type in ["Foundation", "SR Legacy"]:
            confidence = min(1.0, max(0.0, score / 500.0)) # Foundation/SR Legacy are very reliable
            matched_type = "generic_ingredient"
        elif data_type == "Survey (FNDDS)":
            confidence = min(1.0, max(0.0, score / 700.0)) # Good, but perhaps less direct than Foundation
            matched_type = "generic_ingredient"
        else:
            confidence = min(1.0, max(0.0, score / 2000.0)) # Lower confidence for other types or unknown
            matched_type = "estimated_ingredient"

        # Ensure a minimum confidence for any match
        if confidence > 0 and confidence < 0.5: # If a match was made, but score is very low, give it a base confidence
            confidence = 0.5
        elif confidence == 0 and score > 0: # If score is there but confidence calculation yielded 0
            confidence = 0.3


        return NutrientData(
            fdc_id=food_data.get("fdcId"),
            name=food_data.get("description", ""), # This will be overwritten by original query in service layer
            matched_name=food_data.get("description", ""),
            calories=nutrient_values.get(USDA_NUTRIENT_MAP["calories"], 0.0),
            protein=nutrient_values.get(USDA_NUTRIENT_MAP["protein"], 0.0),
            carbohydrates=nutrient_values.get(USDA_NUTRIENT_MAP["carbohydrates"], 0.0),
            fat=nutrient_values.get(USDA_NUTRIENT_MAP["fat"], 0.0),
            fiber=nutrient_values.get(USDA_NUTRIENT_MAP["fiber"], 0.0),
            sugar=nutrient_values.get(USDA_NUTRIENT_MAP["sugar"], 0.0),
            sodium=nutrient_values.get(USDA_NUTRIENT_MAP["sodium"], 0.0),
            saturated_fat=nutrient_values.get(USDA_NUTRIENT_MAP["saturated_fat"], 0.0),
            cholesterol=nutrient_values.get(USDA_NUTRIENT_MAP["cholesterol"], 0.0),
            serving_size=100.0,
            serving_unit="g",
            source="USDA FoodData Central",
            confidence=confidence,
            matched_type=matched_type,
        )

    async def is_available(self) -> bool:
        return bool(self.api_key)

    @property
    def source_name(self) -> str:
        return "USDA FoodData Central"
