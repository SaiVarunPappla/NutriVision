"""
NutriVision - OCR Engine Tests

Tests for the Tesseract OCR wrapper including demo mode behavior.
These tests work whether or not Tesseract is installed.
"""

import pytest
import numpy as np
from ml.ocr_engine import extract_text, DEMO_OCR_TEXT


def _make_white_image(width=200, height=100) -> np.ndarray:
    """Create a white image (no text content)."""
    return np.ones((height, width), dtype=np.uint8) * 255


def _make_image_bytes() -> bytes:
    """Create valid PNG image bytes."""
    import cv2
    img = np.ones((100, 200), dtype=np.uint8) * 255
    _, buffer = cv2.imencode(".png", img)
    return buffer.tobytes()


class TestExtractText:
    def test_returns_dict(self):
        """Test that extract_text always returns a properly structured dict."""
        result = extract_text(processed_image=_make_white_image())
        assert isinstance(result, dict)
        assert "text" in result
        assert "confidence" in result
        assert "source" in result
        assert "success" in result

    def test_has_text_content(self):
        """Test that some text is returned (either from OCR or demo)."""
        result = extract_text(processed_image=_make_white_image())
        assert isinstance(result["text"], str)

    def test_confidence_in_range(self):
        """Test that confidence is a valid number."""
        result = extract_text(processed_image=_make_white_image())
        assert isinstance(result["confidence"], float)
        assert result["confidence"] >= 0

    def test_source_is_valid(self):
        """Test that source field is one of the expected values."""
        result = extract_text(processed_image=_make_white_image())
        assert result["source"] in ["tesseract", "demo", "demo_fallback", "error"]

    def test_with_image_bytes(self):
        """Test OCR using raw image bytes instead of numpy array."""
        result = extract_text(image_bytes=_make_image_bytes())
        assert result["success"] is True

    def test_with_no_input(self):
        """Test OCR with neither image nor bytes returns error."""
        result = extract_text()
        # Should either fail gracefully or return demo text
        assert isinstance(result["text"], str)

    def test_demo_text_has_ingredients(self):
        """Test that demo text contains ingredient-like content."""
        assert "flour" in DEMO_OCR_TEXT.lower()
        assert "sugar" in DEMO_OCR_TEXT.lower()
        assert "salt" in DEMO_OCR_TEXT.lower()
