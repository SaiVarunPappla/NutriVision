"""
NutriVision - Image Preprocessor

Uses OpenCV to preprocess food label images before OCR extraction.
Optimizes images for maximum Tesseract accuracy.

Pipeline:
1. Decode image from raw bytes
2. Convert to grayscale
3. Resize for consistent OCR input
4. Denoise using GaussianBlur
5. Apply adaptive thresholding (handles varying lighting)
6. Optional deskew correction
7. Return processed image as bytes and numpy array
"""

import numpy as np
import cv2
from typing import Optional
import io


def decode_image(image_bytes: bytes) -> Optional[np.ndarray]:
    """
    Decode raw image bytes into an OpenCV numpy array.

    Args:
        image_bytes: Raw JPEG/PNG bytes from file upload

    Returns:
        OpenCV image (BGR numpy array), or None on failure
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception:
        return None


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert a BGR image to grayscale."""
    if len(image.shape) == 2:
        return image  # already grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def resize_image(image: np.ndarray, max_width: int = 1024) -> np.ndarray:
    """
    Resize image to a consistent width while maintaining aspect ratio.
    Larger images produce better OCR but take longer to process.
    """
    h, w = image.shape[:2]
    if w <= max_width:
        return image
    scale = max_width / w
    new_w = max_width
    new_h = int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def denoise(image: np.ndarray) -> np.ndarray:
    """
    Reduce image noise using Gaussian blur.
    A small kernel prevents text from becoming too blurry.
    """
    return cv2.GaussianBlur(image, (3, 3), 0)


def apply_threshold(image: np.ndarray) -> np.ndarray:
    """
    Apply adaptive thresholding to create a clean binary image.
    Adaptive threshold handles uneven lighting on food labels.
    """
    return cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=11,
        C=2,
    )


def sharpen(image: np.ndarray) -> np.ndarray:
    """
    Sharpen the image to make text edges clearer.
    Uses an unsharp masking kernel.
    """
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    return cv2.filter2D(image, -1, kernel)


def deskew(image: np.ndarray) -> np.ndarray:
    """
    Correct slight rotation/skew in the image.
    Uses moment-based angle detection for small angles.
    """
    coords = np.column_stack(np.where(image > 0))
    if len(coords) < 10:
        return image  # not enough points to compute angle

    try:
        angle = cv2.minAreaRect(coords)[-1]

        # Angle correction logic
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Only correct small angles (< 15 degrees)
        if abs(angle) > 15:
            return image

        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(
            image, matrix, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )
    except Exception:
        return image  # return original if deskew fails


def encode_image(image: np.ndarray, fmt: str = ".png") -> bytes:
    """Encode a numpy array back to image bytes."""
    _, buffer = cv2.imencode(fmt, image)
    return buffer.tobytes()


def preprocess_image(image_bytes: bytes) -> dict:
    """
    Full preprocessing pipeline for food label images.

    Args:
        image_bytes: Raw image bytes from upload

    Returns:
        Dict with:
        - 'processed_bytes': preprocessed image as bytes
        - 'processed_image': preprocessed numpy array (for OCR)
        - 'original_size': (width, height) of original
        - 'success': whether preprocessing succeeded
        - 'steps': list of preprocessing steps applied
    """
    steps = []

    # Step 1: Decode
    image = decode_image(image_bytes)
    if image is None:
        return {
            "processed_bytes": image_bytes,
            "processed_image": None,
            "original_size": (0, 0),
            "success": False,
            "steps": ["decode_failed"],
        }

    original_h, original_w = image.shape[:2]
    steps.append("decoded")

    # Step 2: Resize for consistency
    image = resize_image(image, max_width=1024)
    steps.append("resized")

    # Step 3: Convert to grayscale
    gray = to_grayscale(image)
    steps.append("grayscale")

    # Step 4: Denoise
    denoised = denoise(gray)
    steps.append("denoised")

    # Step 5: Sharpen text edges
    sharpened = sharpen(denoised)
    steps.append("sharpened")

    # Step 6: Adaptive threshold
    binary = apply_threshold(sharpened)
    steps.append("thresholded")

    # Step 7: Deskew
    corrected = deskew(binary)
    steps.append("deskewed")

    # Encode result
    processed_bytes = encode_image(corrected)

    return {
        "processed_bytes": processed_bytes,
        "processed_image": corrected,
        "original_size": (original_w, original_h),
        "success": True,
        "steps": steps,
    }
