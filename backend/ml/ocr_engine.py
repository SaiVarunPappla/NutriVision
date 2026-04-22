"""
NutriVision - OCR Engine

Wrapper around Tesseract OCR for text extraction from preprocessed images.
Includes graceful fallback when Tesseract is not installed (demo mode).

Setup (Windows):
    1. Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
    2. Install to default path: C:\\Program Files\\Tesseract-OCR\\
    3. Add to PATH or set TESSERACT_CMD in .env
    4. Verify: tesseract --version

Setup (Linux/Mac):
    sudo apt install tesseract-ocr    (Ubuntu/Debian)
    brew install tesseract             (macOS)

The engine will auto-detect Tesseract on the system PATH.
If not found, it falls back to returning demo text.
"""

import numpy as np
from typing import Optional
from PIL import Image
import io

# Track whether Tesseract is available
_tesseract_available = False
_tesseract_checked = False

try:
    import pytesseract
    _tesseract_available = True
except ImportError:
    _tesseract_available = False


def _check_tesseract() -> bool:
    """
    Check if Tesseract binary is installed and accessible.
    Caches the result after the first check.
    """
    global _tesseract_available, _tesseract_checked

    if _tesseract_checked:
        return _tesseract_available

    _tesseract_checked = True

    if not _tesseract_available:
        print("[OCR] pytesseract package not installed")
        return False

    try:
        # Try setting custom path from config
        from config import settings
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

        # Test if Tesseract binary works
        version = pytesseract.get_tesseract_version()
        print(f"[OCR] Tesseract version {version} detected")
        _tesseract_available = True
        return True
    except Exception as e:
        print(f"[OCR] Tesseract not available: {e}")
        print("[OCR] Running in DEMO MODE - OCR will return sample text")
        _tesseract_available = False
        return False


def is_tesseract_available() -> bool:
    """Public check for Tesseract availability."""
    return _check_tesseract()


# Demo text returned when Tesseract is not installed
DEMO_OCR_TEXT = (
    "INGREDIENTS: Enriched wheat flour (wheat flour, niacin, "
    "reduced iron, thiamine mononitrate, riboflavin, folic acid), "
    "sugar, palm oil, cocoa powder, soy lecithin, salt, "
    "artificial flavor, baking soda."
)


def extract_text(
    processed_image: Optional[np.ndarray] = None,
    image_bytes: Optional[bytes] = None,
) -> dict:
    """
    Extract text from a preprocessed image using Tesseract OCR.

    Can accept either a numpy array (from OpenCV) or raw image bytes.
    Falls back to demo text if Tesseract is not installed.

    Args:
        processed_image: OpenCV numpy array (preferred)
        image_bytes: Raw image bytes (fallback input)

    Returns:
        Dict with:
        - 'text': extracted text string
        - 'confidence': average confidence score (0-100)
        - 'source': 'tesseract' or 'demo'
        - 'success': whether extraction succeeded
    """
    if not _check_tesseract():
        return {
            "text": DEMO_OCR_TEXT,
            "confidence": 95.0,
            "source": "demo",
            "success": True,
        }

    try:
        # Convert numpy array to PIL Image for pytesseract
        if processed_image is not None:
            pil_image = Image.fromarray(processed_image)
        elif image_bytes is not None:
            pil_image = Image.open(io.BytesIO(image_bytes))
        else:
            return {
                "text": "",
                "confidence": 0.0,
                "source": "error",
                "success": False,
            }

        # Tesseract configuration for food label text
        # PSM 6: Assume a uniform block of text
        # OEM 3: Default (LSTM + legacy combined)
        custom_config = r"--oem 3 --psm 6"

        # Extract text
        text = pytesseract.image_to_string(pil_image, config=custom_config)

        # Get confidence data
        data = pytesseract.image_to_data(
            pil_image, config=custom_config, output_type=pytesseract.Output.DICT
        )
        confidences = [
            int(c) for c in data["conf"] if str(c).isdigit() and int(c) > 0
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "text": text.strip(),
            "confidence": round(avg_confidence, 1),
            "source": "tesseract",
            "success": bool(text.strip()),
        }

    except Exception as e:
        print(f"[OCR] Extraction error: {e}")
        # Fallback to demo on error
        return {
            "text": DEMO_OCR_TEXT,
            "confidence": 95.0,
            "source": "demo_fallback",
            "success": True,
        }


def extract_text_with_details(
    processed_image: Optional[np.ndarray] = None,
    image_bytes: Optional[bytes] = None,
) -> dict:
    """
    Extract text with word-level bounding boxes and confidence.
    Useful for debugging and visualization.

    Returns same as extract_text() plus 'words' list with position data.
    """
    result = extract_text(processed_image, image_bytes)

    if result["source"] == "demo" or result["source"] == "demo_fallback":
        # No word-level data in demo mode
        result["words"] = []
        return result

    if not _check_tesseract() or processed_image is None:
        result["words"] = []
        return result

    try:
        pil_image = Image.fromarray(processed_image)
        custom_config = r"--oem 3 --psm 6"
        data = pytesseract.image_to_data(
            pil_image, config=custom_config, output_type=pytesseract.Output.DICT
        )

        words = []
        for i in range(len(data["text"])):
            if data["text"][i].strip():
                words.append({
                    "text": data["text"][i],
                    "confidence": int(data["conf"][i]),
                    "x": data["left"][i],
                    "y": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i],
                })

        result["words"] = words
        return result

    except Exception:
        result["words"] = []
        return result
