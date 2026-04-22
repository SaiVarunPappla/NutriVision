"""
NutriVision - OCR Service

Orchestrates the full image → text extraction pipeline:
1. Receive image bytes from the API route
2. Preprocess with OpenCV (ml/image_preprocessor.py)
3. Extract text with Tesseract OCR (ml/ocr_engine.py)
4. Return structured result with extracted text and metadata

This service sits between the API routes and the ML pipeline,
providing a clean interface for the route handlers.
"""

from ml.image_preprocessor import preprocess_image
from ml.ocr_engine import extract_text, is_tesseract_available


async def extract_text_from_image(image_bytes: bytes) -> dict:
    """
    Full pipeline: image bytes → extracted ingredient text.

    Args:
        image_bytes: Raw bytes of the uploaded food label image

    Returns:
        Dict with:
        - 'text': extracted text string
        - 'confidence': OCR confidence (0-100)
        - 'source': 'tesseract' or 'demo'
        - 'preprocessing': dict of preprocessing metadata
        - 'success': overall success flag
    """
    # Step 1: Preprocess the image with OpenCV
    preprocess_result = preprocess_image(image_bytes)

    if not preprocess_result["success"]:
        # If preprocessing fails, try OCR on the raw image anyway
        ocr_result = extract_text(image_bytes=image_bytes)
        return {
            "text": ocr_result["text"],
            "confidence": ocr_result["confidence"],
            "source": ocr_result["source"],
            "preprocessing": {
                "success": False,
                "steps": preprocess_result["steps"],
                "original_size": preprocess_result["original_size"],
            },
            "success": ocr_result["success"],
        }

    # Step 2: Run OCR on the preprocessed image
    processed_image = preprocess_result["processed_image"]
    ocr_result = extract_text(processed_image=processed_image)

    return {
        "text": ocr_result["text"],
        "confidence": ocr_result["confidence"],
        "source": ocr_result["source"],
        "preprocessing": {
            "success": True,
            "steps": preprocess_result["steps"],
            "original_size": preprocess_result["original_size"],
        },
        "success": ocr_result["success"],
    }


async def get_ocr_status() -> dict:
    """
    Get the current status of the OCR engine.
    Useful for health checks and debugging.
    """
    return {
        "tesseract_available": is_tesseract_available(),
        "mode": "tesseract" if is_tesseract_available() else "demo",
    }
