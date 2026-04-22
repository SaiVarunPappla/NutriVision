"""
NutriVision - Open Food Facts API Integration
"""
import httpx
from typing import Optional
from integrations.base_nutrition_api import BaseNutritionAPI, NutrientData
from config import settings

class OpenFoodFactsAPI(BaseNutritionAPI):
    def __init__(self):
        self.base_url = settings.openfoodfacts_base_url or "https://world.openfoodfacts.org"

    async def search_food(self, query: str, max_results: int = 5) -> list[dict]:
        url = f"{self.base_url}/cgi/search.pl"
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": max_results
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            products = data.get("products", [])
            results = []
            for p in products:
                product_name = p.get("product_name", "")
                generic_name = p.get("generic_name", "")
                matched_name = product_name or generic_name or "Unknown"

                confidence = 0.0
                matched_type = "no_match"

                if product_name:
                    confidence = 0.8 # High confidence for branded product name match
                    matched_type = "branded_product"
                elif generic_name:
                    confidence = 0.6 # Moderate confidence for generic name match
                    matched_type = "generic_ingredient"
                
                results.append({
                    "food_id": p.get("code"),
                    "description": matched_name, # Use for a consistent field across search results
                    "source": "OpenFoodFacts",
                    "confidence": confidence,
                    "matched_type": matched_type,
                })
            return results
        except Exception as e:
            print(f"[OpenFoodFacts] Search error: {e}")
            return []

    async def get_food_details(self, food_id: str) -> Optional[NutrientData]:
        url = f"{self.base_url}/api/v0/product/{food_id}.json"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            
            product = data.get("product", {})
            nutriments = product.get("nutriments", {})
            
            matched_name = product.get("product_name", product.get("generic_name", food_id))
            matched_type = "branded_product" if product.get("product_name") else "generic_ingredient"
            confidence = 0.9 # High confidence for a direct food_id lookup

            return NutrientData(
                name=matched_name, # This will be overwritten by original query in service layer
                matched_name=matched_name,
                calories=float(nutriments.get("energy-kcal_100g", 0.0)),
                protein=float(nutriments.get("proteins_100g", 0.0)),
                carbohydrates=float(nutriments.get("carbohydrates_100g", 0.0)),
                fat=float(nutriments.get("fat_100g", 0.0)),
                fiber=float(nutriments.get("fiber_100g", 0.0)),
                sugar=float(nutriments.get("sugars_100g", 0.0)),
                sodium=float(nutriments.get("sodium_100g", 0.0)) * 1000, # g to mg
                saturated_fat=float(nutriments.get("saturated-fat_100g", 0.0)),
                cholesterol=float(nutriments.get("cholesterol_100g", 0.0)),
                source="OpenFoodFacts",
                confidence=confidence,
                matched_type=matched_type,
            )
        except Exception as e:
            print(f"[OpenFoodFacts] Detail error: {e}")
            return None

    async def is_available(self) -> bool:
        return True

    @property
    def source_name(self) -> str:
        return "OpenFoodFacts"
