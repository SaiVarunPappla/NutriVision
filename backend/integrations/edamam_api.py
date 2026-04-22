"""
NutriVision - Edamam API Integration (Optional / Pluggable)

OPTIONAL nutrition data source. NOT required for the app to work.
USDA FoodData Central is the primary working API.

This demonstrates the pluggable API architecture using the Strategy pattern.
If Edamam credentials are provided in .env, this can be used as a fallback.

API Documentation: https://developer.edamam.com/edamam-docs-nutrition-api
API Signup: https://developer.edamam.com/ (free tier: 100 req/day)
"""

import httpx
from typing import Optional
from integrations.base_nutrition_api import BaseNutritionAPI, NutrientData
from config import settings

REQUEST_TIMEOUT = 10.0


class EdamamNutritionAPI(BaseNutritionAPI):
    """
    Edamam Nutrition API client (OPTIONAL / PLUGGABLE).
    Only active when credentials are provided in .env.
    """

    def __init__(self):
        self.app_id = settings.edamam_app_id
        self.app_key = settings.edamam_app_key
        self.base_url = settings.edamam_base_url

    async def search_food(self, query: str, max_results: int = 5) -> list[dict]:
        """Search Edamam for food items. Only works if credentials are set."""
        if not await self.is_available():
            return []

        url = f"{self.base_url}/food-database/v2/parser"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "ingr": query,
        }

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            hints = data.get("hints", [])[:max_results]
            return [
                {
                    "food_id": h.get("food", {}).get("foodId", ""),
                    "label": h.get("food", {}).get("label", ""),
                    "category": h.get("food", {}).get("category", ""),
                    "source": "Edamam",
                    "confidence": 0.9, # High confidence for a direct hit/hint from parser
                    "matched_type": "generic_ingredient",
                }
                for h in hints
            ]
        except Exception as e:
            print(f"[Edamam] Search error: {e}")
            return []

    async def get_food_details(self, food_id: str, food_label: str = "") -> Optional[NutrientData]:
        """
        Get nutrition from Edamam. Uses the nutrients endpoint.
        Note: Edamam uses string food IDs.
        """
        if not await self.is_available():
            return None

        url = f"{self.base_url}/food-database/v2/nutrients"
        params = {"app_id": self.app_id, "app_key": self.app_key}
        payload = {
            "ingredients": [
                {"quantity": 100, "measureURI": "g", "foodId": food_id} # food_id is already a string
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(url, params=params, json=payload)
                response.raise_for_status()
                data = response.json()

            total = data.get("totalNutrients", {})
            
            matched_name = food_label if food_label else food_id
            confidence = 0.9 # High confidence for a direct ID lookup
            matched_type = "generic_ingredient"

            return NutrientData(
                name=matched_name, # This will be overwritten by original query in service layer
                matched_name=matched_name,
                calories=total.get("ENERC_KCAL", {}).get("quantity", 0),
                protein=total.get("PROCNT", {}).get("quantity", 0),
                carbohydrates=total.get("CHOCDF", {}).get("quantity", 0),
                fat=total.get("FAT", {}).get("quantity", 0),
                fiber=total.get("FIBTG", {}).get("quantity", 0),
                sugar=total.get("SUGAR", {}).get("quantity", 0),
                sodium=total.get("NA", {}).get("quantity", 0),
                saturated_fat=total.get("FASAT", {}).get("quantity", 0),
                cholesterol=total.get("CHOLE", {}).get("quantity", 0),
                source="Edamam",
                confidence=confidence,
                matched_type=matched_type,
            )
        except Exception as e:
            print(f"[Edamam] Detail error: {e}")
            return None

    async def is_available(self) -> bool:
        """Check if Edamam credentials are configured."""
        return settings.is_edamam_configured

    @property
    def source_name(self) -> str:
        return "Edamam"
