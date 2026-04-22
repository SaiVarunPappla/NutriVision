"""
NutriVision - NLP Processor Tests

Comprehensive tests for the ingredient text NLP pipeline.
Tests each stage: section detection, splitting, cleaning, normalization.
"""

import pytest
from ml.nlp_processor import (
    find_ingredient_section,
    split_ingredients,
    clean_ingredient,
    normalize_ingredient,
    process_ingredient_text,
    extract_potential_allergen_text,
)


# ===========================
# Test Data
# ===========================

SAMPLE_LABEL_TEXT = (
    "Chocolate Cookies\n"
    "Net Wt. 200g\n"
    "INGREDIENTS: Enriched wheat flour (wheat flour, niacin, "
    "reduced iron, thiamine mononitrate, riboflavin, folic acid), "
    "sugar, palm oil, cocoa powder (10%), soy lecithin, salt, "
    "artificial flavor, baking soda.\n"
    "Allergen Warning: Contains wheat, soy.\n"
    "Manufactured by Example Foods Inc."
)

SIMPLE_TEXT = "sugar, flour, butter, eggs, vanilla extract, baking powder, salt"

TEXT_WITH_PERCENTAGES = "water (60%), sugar (15%), wheat flour (10%), salt (2%)"

TEXT_WITH_ENUMBERS = "sugar, E621, flour, E330, palm oil, E471"


# ===========================
# Section Detection Tests
# ===========================

class TestFindIngredientSection:
    def test_finds_ingredients_after_header(self):
        """Test extraction of ingredients after 'INGREDIENTS:' header."""
        result = find_ingredient_section(SAMPLE_LABEL_TEXT)
        assert "sugar" in result.lower()
        assert "wheat flour" in result.lower()

    def test_removes_footer_text(self):
        """Test that manufacturer/allergen footer is removed."""
        result = find_ingredient_section(SAMPLE_LABEL_TEXT)
        assert "manufactured" not in result.lower()

    def test_plain_text_passthrough(self):
        """Test that plain ingredient text without headers passes through."""
        result = find_ingredient_section(SIMPLE_TEXT)
        assert "sugar" in result

    def test_empty_text(self):
        """Test handling of empty input."""
        result = find_ingredient_section("")
        assert result == ""


# ===========================
# Splitting Tests
# ===========================

class TestSplitIngredients:
    def test_comma_separated(self):
        """Test splitting comma-separated ingredients."""
        result = split_ingredients(SIMPLE_TEXT)
        assert len(result) == 7
        assert "sugar" in result

    def test_semicolon_separated(self):
        """Test splitting semicolon-separated ingredients."""
        result = split_ingredients("sugar; flour; salt")
        assert len(result) == 3

    def test_newline_separated(self):
        """Test splitting newline-separated ingredients."""
        result = split_ingredients("sugar\nflour\nsalt")
        assert len(result) == 3

    def test_full_label_text(self):
        """Test splitting from a full food label."""
        result = split_ingredients(SAMPLE_LABEL_TEXT)
        assert len(result) >= 5  # Should find multiple ingredients

    def test_empty_input(self):
        """Test splitting empty text."""
        result = split_ingredients("")
        assert result == []

    def test_filters_very_short_items(self):
        """Test that single-character artifacts are filtered."""
        result = split_ingredients("sugar, , , salt, a, flour")
        # 'a' should be filtered (length <= 1)
        names = [r.lower() for r in result]
        assert "sugar" in names
        assert "salt" in names


# ===========================
# Cleaning Tests
# ===========================

class TestCleanIngredient:
    def test_lowercase(self):
        """Test that ingredient names are lowercased."""
        assert clean_ingredient("SUGAR") == "sugar"

    def test_removes_parenthetical(self):
        """Test removal of parenthetical content."""
        result = clean_ingredient("flour (wheat, enriched)")
        assert "wheat" not in result
        assert "flour" in result

    def test_removes_percentage(self):
        """Test removal of percentage values."""
        result = clean_ingredient("sugar 15%")
        assert "15" not in result
        assert "sugar" in result

    def test_removes_quantity(self):
        """Test removal of quantity indicators."""
        result = clean_ingredient("2g salt")
        assert "2g" not in result
        assert "salt" in result

    def test_removes_enumbers(self):
        """Test removal of E-number additives."""
        result = clean_ingredient("E621")
        assert result == ""

    def test_strips_whitespace(self):
        """Test stripping of extra whitespace."""
        result = clean_ingredient("  sugar  ")
        assert result == "sugar"

    def test_empty_input(self):
        """Test handling of empty string."""
        assert clean_ingredient("") == ""

    def test_removes_brackets(self):
        """Test removal of bracketed content."""
        result = clean_ingredient("oil [palm]")
        assert "palm" not in result
        assert "oil" in result

    def test_preserves_meaningful_names(self):
        """Test that actual ingredient names are preserved."""
        assert "cocoa" in clean_ingredient("cocoa powder")
        assert "salt" in clean_ingredient("salt")
        assert "vanilla" in clean_ingredient("vanilla extract")


# ===========================
# Normalization Tests
# ===========================

class TestNormalizeIngredient:
    def test_enriched_flour(self):
        """Test normalization of 'enriched wheat flour'."""
        result = normalize_ingredient("enriched wheat flour")
        assert result == "wheat flour"

    def test_cane_sugar(self):
        """Test normalization of sugar variants."""
        assert normalize_ingredient("cane sugar") == "sugar"
        assert normalize_ingredient("granulated sugar") == "sugar"

    def test_sea_salt(self):
        """Test normalization of salt variants."""
        assert normalize_ingredient("sea salt") == "salt"
        assert normalize_ingredient("kosher salt") == "salt"

    def test_baking_soda(self):
        """Test normalization of sodium bicarbonate."""
        assert normalize_ingredient("sodium bicarbonate") == "baking soda"

    def test_unknown_ingredient_passthrough(self):
        """Test that unknown ingredients pass through unchanged."""
        assert normalize_ingredient("xanthan gum") == "xanthan gum"

    def test_soy_lecithin(self):
        """Test that soy lecithin is preserved (important for allergens)."""
        assert normalize_ingredient("soy lecithin") == "soy lecithin"


# ===========================
# Full Pipeline Tests
# ===========================

class TestProcessIngredientText:
    def test_simple_list(self):
        """Test processing a simple comma-separated list."""
        result = process_ingredient_text(SIMPLE_TEXT)
        assert len(result) >= 5
        names = [r["normalized_name"] for r in result]
        assert "sugar" in names
        assert "salt" in names

    def test_full_label(self):
        """Test processing a full food label text."""
        result = process_ingredient_text(SAMPLE_LABEL_TEXT)
        assert len(result) >= 5
        names = [r["normalized_name"] for r in result]
        assert "sugar" in names

    def test_deduplication(self):
        """Test that duplicate ingredients are removed."""
        result = process_ingredient_text("sugar, Sugar, SUGAR, flour")
        names = [r["normalized_name"] for r in result]
        assert names.count("sugar") == 1

    def test_position_assigned(self):
        """Test that positions are assigned sequentially."""
        result = process_ingredient_text("sugar, flour, salt")
        positions = [r["position"] for r in result]
        assert positions == [1, 2, 3]

    def test_preserves_original_name(self):
        """Test that original (raw) name is preserved."""
        result = process_ingredient_text("Enriched Wheat Flour, Sugar")
        assert result[0]["name"] != result[0]["normalized_name"] or \
               result[0]["name"].lower() == result[0]["normalized_name"]

    def test_empty_input(self):
        """Test with empty input."""
        assert process_ingredient_text("") == []
        assert process_ingredient_text(None) == []

    def test_with_percentages(self):
        """Test that percentages are cleaned out."""
        result = process_ingredient_text(TEXT_WITH_PERCENTAGES)
        for item in result:
            assert "%" not in item["normalized_name"]

    def test_with_enumbers(self):
        """Test that E-numbers are filtered out."""
        result = process_ingredient_text(TEXT_WITH_ENUMBERS)
        names = [r["normalized_name"] for r in result]
        assert not any(n.startswith("e6") or n.startswith("e3") or n.startswith("e4")
                       for n in names)

    def test_returns_dict_format(self):
        """Test that each result has the expected keys."""
        result = process_ingredient_text("sugar, flour")
        for item in result:
            assert "name" in item
            assert "normalized_name" in item
            assert "position" in item


# ===========================
# Allergen Text Extraction
# ===========================

class TestExtractAllergenText:
    def test_finds_contains_warning(self):
        """Test extraction of 'Contains:' allergen text."""
        result = extract_potential_allergen_text(
            "Ingredients: flour, sugar. Contains: wheat, soy, milk."
        )
        assert result is not None
        assert "wheat" in result.lower()

    def test_finds_may_contain(self):
        """Test extraction of 'May contain:' text."""
        result = extract_potential_allergen_text(
            "May contain: peanuts, tree nuts."
        )
        assert result is not None
        assert "peanut" in result.lower()

    def test_returns_none_when_absent(self):
        """Test that None is returned when no allergen text exists."""
        result = extract_potential_allergen_text("sugar, flour, salt")
        assert result is None
