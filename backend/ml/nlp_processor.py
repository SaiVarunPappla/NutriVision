"""
NutriVision - NLP Processor

Natural Language Processing pipeline for ingredient text cleaning
and normalization. Transforms raw OCR/user text into clean, standardized
ingredient names suitable for USDA API lookup.

Pipeline:
1. Find and isolate the ingredient section from raw text
2. Split into individual ingredients (comma, semicolon, newline)
3. Clean each ingredient:
   - Lowercase
   - Remove percentages (e.g., "sugar (5%)" → "sugar")
   - Remove parenthetical details (e.g., "flour (wheat, enriched)" → "flour")
   - Remove quantity indicators (e.g., "2g salt" → "salt")
   - Remove E-number additives (e.g., "E621" → removed)
   - Remove common noise words
   - Strip extra whitespace
4. Normalize ingredient names (map common variations)
5. Deduplicate
6. Return ordered list
"""

import re
from typing import Optional


# ============================================================
# INGREDIENT SECTION DETECTION
# ============================================================

# Patterns that indicate the start of an ingredients list
INGREDIENT_HEADERS = [
    r"ingredients?\s*:",
    r"contains?\s*:",
    r"made\s+with\s*:",
    r"composition\s*:",
]


def find_ingredient_section(raw_text: str) -> str:
    """
    Extract just the ingredients section from a longer text block.
    Food labels often have other text (brand name, nutrition facts, etc.)
    """
    text = raw_text.strip()

    # Try to find "Ingredients:" header
    for pattern in INGREDIENT_HEADERS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Take everything after the header
            text = text[match.end():]
            break

    # Remove common footer text that appears after ingredients
    stop_patterns = [
        r"nutrition\s+facts",
        r"allergen\s+(info|warning|statement)",
        r"manufactured\s+by",
        r"distributed\s+by",
        r"best\s+before",
        r"store\s+in",
        r"net\s+w(eigh)?t",
        r"serving\s+size",
    ]
    for pattern in stop_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            text = text[:match.start()]

    return text.strip()


# ============================================================
# TEXT SPLITTING
# ============================================================

def split_ingredients(raw_text: str) -> list[str]:
    """
    Split raw ingredient text into individual ingredient strings.
    Handles commas, semicolons, newlines, and period-separated lists.
    """
    text = find_ingredient_section(raw_text)

    if not text:
        return []

    # Replace common separators with a standard delimiter
    text = re.sub(r"[;\n\r]+", ",", text)

    # Split by comma
    items = text.split(",")

    # Clean and filter empty items
    result = []
    for item in items:
        cleaned = item.strip().rstrip(".")
        if cleaned and len(cleaned) > 1:
            result.append(cleaned)

    return result


# ============================================================
# INDIVIDUAL INGREDIENT CLEANING
# ============================================================

# Patterns to remove from ingredient names
REMOVE_PATTERNS = [
    r"\([^)]*\)",             # Parenthetical content: "flour (wheat)" → "flour"
    r"\[[^\]]*\]",            # Bracketed content: "sugar [organic]" → "sugar"
    r"\{[^}]*\}",             # Braced content
    r"\d+\.?\d*\s*%",         # Percentages: "5.2%" → ""
    r"\d+\.?\d*\s*(g|mg|kg|ml|l|oz|lb|mcg)\b",  # Quantities: "2g" → ""
    r"\b[eE]\d{3,4}\b",      # E-numbers: "E621" → ""
    r"\*+",                   # Asterisks
    r"†+",                    # Daggers
    r"^[\d\.\s]+",            # Leading numbers: "1. sugar" → "sugar"
]

# Words to remove (not actual ingredients)
NOISE_WORDS = {
    "and", "or", "with", "from", "less", "than", "more",
    "may", "contain", "contains", "traces", "of", "added",
    "for", "as", "an", "a", "the", "to", "in", "on",
    "organic", "natural", "pure", "raw", "fresh",
    "certified", "grade", "quality",
}

# Common ingredient name normalizations
NORMALIZATIONS = {
    "enriched wheat flour": "wheat flour",
    "all purpose flour": "wheat flour",
    "all-purpose flour": "wheat flour",
    "whole wheat flour": "whole wheat flour",
    "cane sugar": "sugar",
    "raw sugar": "sugar",
    "brown sugar": "brown sugar",
    "granulated sugar": "sugar",
    "powdered sugar": "sugar",
    "confectioners sugar": "sugar",
    "high fructose corn syrup": "high fructose corn syrup",
    "corn syrup solids": "corn syrup",
    "palm kernel oil": "palm oil",
    "partially hydrogenated": "hydrogenated oil",
    "canola oil": "canola oil",
    "vegetable oil": "vegetable oil",
    "soybean oil": "soybean oil",
    "sunflower oil": "sunflower oil",
    "olive oil": "olive oil",
    "sea salt": "salt",
    "kosher salt": "salt",
    "iodized salt": "salt",
    "table salt": "salt",
    "nonfat milk": "skim milk",
    "skimmed milk": "skim milk",
    "whole milk": "whole milk",
    "milk powder": "milk powder",
    "dried milk": "milk powder",
    "soy lecithin": "soy lecithin",
    "cocoa powder": "cocoa",
    "baking soda": "baking soda",
    "sodium bicarbonate": "baking soda",
    "citric acid": "citric acid",
    "ascorbic acid": "vitamin c",
    "tocopherols": "vitamin e",
    "riboflavin": "vitamin b2",
    "thiamine": "vitamin b1",
    "niacin": "vitamin b3",
    "folic acid": "vitamin b9",
    "pyridoxine": "vitamin b6",
}


def clean_ingredient(raw_name: str) -> str:
    """
    Clean a single raw ingredient name.
    Removes noise, normalizes text, and strips unwanted content.
    """
    text = raw_name.strip()

    if not text:
        return ""

    # Lowercase
    text = text.lower()

    # Apply removal patterns
    for pattern in REMOVE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Remove noise words only if they appear alone at boundaries
    words = text.split()
    cleaned_words = [w for w in words if w not in NOISE_WORDS or len(words) <= 2]
    text = " ".join(cleaned_words)

    # Clean up whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Remove trailing/leading punctuation
    text = text.strip(".,;:-–—")

    return text.strip()


def normalize_ingredient(raw_name: str) -> str:
    """
    Clean AND normalize a single ingredient name.
    First cleans, then applies normalization mapping.
    """
    cleaned = clean_ingredient(raw_name)

    if not cleaned:
        return ""

    # Check normalization map
    normalized = NORMALIZATIONS.get(cleaned, cleaned)

    return normalized


# ============================================================
# FULL PIPELINE
# ============================================================

def process_ingredient_text(raw_text: str) -> list[dict]:
    """
    Full NLP pipeline: raw text → list of cleaned, normalized ingredients.

    Args:
        raw_text: Raw ingredient text from OCR or user input

    Returns:
        List of dicts with 'name' (original), 'normalized_name', 'position'
    """
    if not raw_text or not raw_text.strip():
        return []

    # Split into individual ingredients
    raw_items = split_ingredients(raw_text)

    # Clean, normalize, and deduplicate
    seen = set()
    ingredients = []
    position = 1

    for raw_name in raw_items:
        cleaned = clean_ingredient(raw_name)
        normalized = normalize_ingredient(raw_name)

        # Skip empty or duplicate ingredients
        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        ingredients.append({
            "name": raw_name.strip(),
            "normalized_name": normalized,
            "position": position,
        })
        position += 1

    return ingredients


def extract_potential_allergen_text(raw_text: str) -> Optional[str]:
    """
    Extract allergen warning text if present (e.g., "Contains: milk, wheat, soy").
    This is sometimes separate from the ingredients list.
    """
    patterns = [
        r"contains?\s*:\s*(.+?)(?:\.|$)",
        r"allergen\s*(?:info|warning|statement)\s*:\s*(.+?)(?:\.|$)",
        r"may\s+contain\s*:\s*(.+?)(?:\.|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None
