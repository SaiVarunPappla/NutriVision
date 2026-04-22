"""
NutriVision - Nutrition Service

Orchestrates nutrition data lookup for parsed ingredients:
1. Receives list of normalized ingredients from the parser
2. Tries OpenFoodFacts (if available)
3. Tries USDA FoodData Central API (Primary)
4. Tries API-Ninjas as a fallback
5. Falls back to Demo data if all APIs fail
6. Aggregates per-ingredient nutrition into totals
"""

from typing import Optional, Tuple, List
from models.nutrition import NutritionSummary, NutrientDetail
from models.ingredient import IngredientBase
from integrations.usda_api import USDANutritionAPI
from integrations.api_ninjas_api import ApiNinjasNutritionAPI
from integrations.openfoodfacts_api import OpenFoodFactsAPI
from integrations.edamam_api import EdamamNutritionAPI
from integrations.base_nutrition_api import NutrientData
from utils.constants import DAILY_VALUES
from utils.helpers import calculate_daily_pct
from services.reference_nutrition import get_reference_nutrition
import asyncio

# Confidence thresholds
MIN_BRANDED_CONFIDENCE = 0.7
MIN_INGREDIENT_CONFIDENCE = 0.6
MIN_AGGREGATION_CONFIDENCE = 0.5

# Singleton API clients
_usda_client = USDANutritionAPI()
_api_ninjas_client = ApiNinjasNutritionAPI()
_off_client = OpenFoodFactsAPI()
_edamam_client = EdamamNutritionAPI()

# Demo nutrition data
MOCK_DATA = {
    "coffee": NutrientData(calories=2, protein=0.3, carbohydrates=0, fat=0, fiber=0, sugar=0, sodium=2, source="Mock Data"),
    "water": NutrientData(calories=0, protein=0, carbohydrates=0, fat=0, fiber=0, sugar=0, sodium=0, source="Mock Data"),
    "egg": NutrientData(calories=70, protein=6.0, carbohydrates=0.6, fat=5.0, fiber=0, sugar=0.1, sodium=70, source="Mock Data"),
    "bread": NutrientData(calories=80, protein=3.0, carbohydrates=15, fat=1.0, fiber=1.0, sugar=1.0, sodium=150, source="Mock Data"),
    "chicken breast": NutrientData(calories=165, protein=31.0, carbohydrates=0, fat=3.6, fiber=0, sugar=0, sodium=74, source="Mock Data"),
}

def _get_demo_nutrition(name: str) -> NutrientData:
    lower_name = name.lower()
    for key, data in MOCK_DATA.items():
        if key in lower_name:
            return NutrientData(
                name=name, matched_name=key, calories=data.calories,
                protein=data.protein, carbohydrates=data.carbohydrates,
                fat=data.fat, fiber=data.fiber, sugar=data.sugar,
                sodium=data.sodium, source=data.source,
                confidence=0.2, matched_type="estimated_ingredient"
            )
    return get_reference_nutrition(name)

async def lookup_branded_nutrition(product_name: str) -> Tuple[NutritionSummary, List[NutrientData], str]:
    if not product_name or not product_name.strip():
        return NutritionSummary(overall_matched_type="no_match", warning_messages=["No product name provided for branded lookup."]), [], "No product name provided."

    # USDA
    usda_branded_data = await _usda_client.search_and_get_nutrition(product_name, is_branded_search=True)
    if usda_branded_data and usda_branded_data.confidence >= MIN_BRANDED_CONFIDENCE:
        product_nutrient_data = [usda_branded_data]
        summary = _aggregate_nutrition([{"name": product_name, "nutrition": usda_branded_data}])
        summary.overall_matched_name = usda_branded_data.matched_name
        summary.overall_nutrition_source = usda_branded_data.source
        summary.overall_confidence = usda_branded_data.confidence
        summary.overall_matched_type = "branded_product"
        return summary, product_nutrient_data, f"Branded match found via {usda_branded_data.source}."

    # OpenFoodFacts
    if await _off_client.is_available():
        off_search_results = await _off_client.search_food(product_name, max_results=1)
        if off_search_results and off_search_results[0].get("confidence", 0.0) >= MIN_BRANDED_CONFIDENCE:
            off_data = await _off_client.get_food_details(off_search_results[0].get("food_id"))
            if off_data and off_data.confidence >= MIN_BRANDED_CONFIDENCE:
                summary = _aggregate_nutrition([{"name": product_name, "nutrition": off_data}])
                return summary, [off_data], f"Branded match found via {off_data.source}."

    # API-Ninjas
    if await _api_ninjas_client.is_available():
        results = await _api_ninjas_client.search_food(product_name, max_results=1)
        if results and results[0].get("confidence", 0.0) >= MIN_BRANDED_CONFIDENCE * 0.8:
            data = await _api_ninjas_client.get_food_details(results[0].get("description"))
            if data and data.confidence >= MIN_BRANDED_CONFIDENCE * 0.8:
                summary = _aggregate_nutrition([{"name": product_name, "nutrition": data}])
                return summary, [data], f"Estimated branded match found via {data.source}."

    return NutritionSummary(overall_matched_name=product_name, overall_matched_type="no_match", overall_confidence=0.0), [], "No confident branded product match found."

# Optimized lookup to avoid slow sequential API calls
async def lookup_nutrition(ingredients: list[IngredientBase], use_api: bool = True) -> Tuple[NutritionSummary, list[dict], str]:
    if not ingredients:
        return NutritionSummary(), [], "No ingredients to analyze."

    if not use_api:
        per_ingredient = [{"name": ing.normalized_name, "nutrition": _get_demo_nutrition(ing.normalized_name), "source": "demo"} for ing in ingredients]
        return _aggregate_nutrition(per_ingredient), per_ingredient, "Skipped API lookup."

    async def _get_single_ingredient_nutrition(name: str):
        # 1. Open Food Facts
        off_results = await _off_client.search_food(name, max_results=1)
        if off_results:
            nutrient_data = await _off_client.get_food_details(off_results[0]["food_id"])
            if nutrient_data: return nutrient_data, "OpenFoodFacts"

        # 2. USDA
        nutrient_data = await _usda_client.search_and_get_nutrition(name)
        if nutrient_data: return nutrient_data, "USDA"

        # 3. API-Ninjas
        nutrient_data = await _lookup_single_ninjas(name)
        if nutrient_data: return nutrient_data, "API-Ninjas"

        # 4. Demo
        return _get_demo_nutrition(name), "demo"

    # Run API lookups concurrently for all ingredients
    tasks = [_get_single_ingredient_nutrition(ing.normalized_name) for ing in ingredients]
    results = await asyncio.gather(*tasks)

    per_ingredient = []
    for i, (nutrient_data, source_name) in enumerate(results):
        per_ingredient.append({
            "name": ingredients[i].normalized_name,
            "nutrition": nutrient_data,
            "source": source_name,
        })

    summary = _aggregate_nutrition(per_ingredient)
    return summary, per_ingredient, "Analysis completed using parallel multi-source lookup."


async def _lookup_single_ninjas(name):
    try:
        results = await _api_ninjas_client.search_food(name, max_results=1)
        if results:
            return await _api_ninjas_client.get_food_details(results[0]["description"])
    except: return None
    return None

def _aggregate_nutrition(per_ingredient: List[dict]) -> NutritionSummary:
    count = len(per_ingredient)
    if count == 0: return NutritionSummary()

    totals = {"calories": 0.0, "protein": 0.0, "carbohydrates": 0.0, "fat": 0.0, "fiber": 0.0, "sugar": 0.0, "sodium": 0.0, "saturated_fat": 0.0, "cholesterol": 0.0}
    for item in per_ingredient:
        nd = item.get("nutrition")
        if nd:
            totals["calories"] += nd.calories
            totals["protein"] += nd.protein
            totals["carbohydrates"] += nd.carbohydrates
            totals["fat"] += nd.fat
            totals["fiber"] += nd.fiber
            totals["sugar"] += nd.sugar
            totals["sodium"] += nd.sodium
            totals["saturated_fat"] += nd.saturated_fat
            totals["cholesterol"] += nd.cholesterol

    for key in totals: totals[key] = round(totals[key] / count, 1)

    return NutritionSummary(
        total_calories=totals["calories"],
        protein=NutrientDetail(value=totals["protein"], unit="g", daily_pct=calculate_daily_pct(totals["protein"], DAILY_VALUES["protein"])),
        carbohydrates=NutrientDetail(value=totals["carbohydrates"], unit="g", daily_pct=calculate_daily_pct(totals["carbohydrates"], DAILY_VALUES["carbohydrates"])),
        fat=NutrientDetail(value=totals["fat"], unit="g", daily_pct=calculate_daily_pct(totals["fat"], DAILY_VALUES["fat"])),
        fiber=NutrientDetail(value=totals["fiber"], unit="g", daily_pct=calculate_daily_pct(totals["fiber"], DAILY_VALUES["fiber"])),
        sugar=NutrientDetail(value=totals["sugar"], unit="g", daily_pct=calculate_daily_pct(totals["sugar"], DAILY_VALUES["sugar"])),
        sodium=NutrientDetail(value=totals["sodium"], unit="mg", daily_pct=calculate_daily_pct(totals["sodium"], DAILY_VALUES["sodium"])),
        saturated_fat=NutrientDetail(value=totals["saturated_fat"], unit="g", daily_pct=calculate_daily_pct(totals["saturated_fat"], DAILY_VALUES["saturated_fat"])),
        cholesterol=NutrientDetail(value=totals["cholesterol"], unit="mg", daily_pct=calculate_daily_pct(totals["cholesterol"], DAILY_VALUES["cholesterol"])),
    )
