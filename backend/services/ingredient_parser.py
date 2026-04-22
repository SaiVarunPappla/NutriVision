"""
NutriVision - Ingredient Parser Service

Parses raw text (from OCR or user input) into a clean, structured list
of ingredients using the NLP processor.

This service sits between the API routes and the NLP pipeline,
providing a clean interface with proper Pydantic model output.
"""

from models.ingredient import IngredientBase
from ml.nlp_processor import process_ingredient_text, extract_potential_allergen_text
from typing import Optional


async def parse_ingredients(raw_text: str) -> list[IngredientBase]:
    """
    Parse raw ingredient text into structured IngredientBase objects.

    Uses the NLP pipeline to:
    - Find the ingredient section in the text
    - Split into individual ingredients
    - Clean and normalize each name
    - Deduplicate

    Args:
        raw_text: Raw ingredient string from OCR or user text input

    Returns:
        List of IngredientBase objects with name, normalized_name, position
    """
    if not raw_text or not raw_text.strip():
        return []

    # Run the NLP pipeline
    parsed = process_ingredient_text(raw_text)

    # Convert to Pydantic models
    ingredients = [
        IngredientBase(
            name=item["name"],
            normalized_name=item["normalized_name"],
            position=item["position"],
        )
        for item in parsed
    ]

    return ingredients


async def parse_ingredients_with_metadata(raw_text: str) -> dict:
    """
    Parse ingredients and return additional metadata useful for analysis.

    Returns:
        Dict with:
        - 'ingredients': list of IngredientBase objects
        - 'count': number of unique ingredients found
        - 'allergen_warning': any separate allergen text found
        - 'raw_text': the original input text
    """
    ingredients = await parse_ingredients(raw_text)
    allergen_text = extract_potential_allergen_text(raw_text)

    return {
        "ingredients": ingredients,
        "count": len(ingredients),
        "allergen_warning": allergen_text,
        "raw_text": raw_text,
    }
