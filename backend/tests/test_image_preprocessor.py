"""
NutriVision - Image Preprocessor Tests

Tests for OpenCV-based image preprocessing functions.
Uses synthetic test images created with numpy.
"""

import pytest
import numpy as np
from ml.image_preprocessor import (
    decode_image,
    to_grayscale,
    resize_image,
    denoise,
    apply_threshold,
    sharpen,
    deskew,
    encode_image,
    preprocess_image,
)


def _make_test_image(width=200, height=100, channels=3) -> np.ndarray:
    """Create a simple synthetic BGR test image."""
    image = np.zeros((height, width, channels), dtype=np.uint8)
    # Add some white text-like features
    image[20:80, 30:170] = 200  # bright rectangle
    image[40:60, 50:150] = 50   # darker inner area (simulates text)
    return image


def _make_grayscale_image(width=200, height=100) -> np.ndarray:
    """Create a synthetic grayscale test image."""
    image = np.zeros((height, width), dtype=np.uint8)
    image[20:80, 30:170] = 200
    image[40:60, 50:150] = 50
    return image


class TestDecodeImage:
    def test_valid_image(self):
        """Test decoding a valid PNG image."""
        img = _make_test_image()
        _, buffer = __import__("cv2").imencode(".png", img)
        result = decode_image(buffer.tobytes())
        assert result is not None
        assert len(result.shape) == 3

    def test_invalid_bytes(self):
        """Test decoding invalid bytes returns None."""
        result = decode_image(b"not an image")
        assert result is None

    def test_empty_bytes(self):
        """Test decoding empty bytes returns None."""
        result = decode_image(b"")
        assert result is None


class TestToGrayscale:
    def test_bgr_to_gray(self):
        """Test converting BGR image to grayscale."""
        img = _make_test_image()
        gray = to_grayscale(img)
        assert len(gray.shape) == 2

    def test_already_gray(self):
        """Test that grayscale image passes through unchanged."""
        img = _make_grayscale_image()
        gray = to_grayscale(img)
        assert len(gray.shape) == 2
        assert np.array_equal(img, gray)


class TestResizeImage:
    def test_large_image_resized(self):
        """Test that images wider than max_width are resized."""
        img = _make_test_image(width=2000, height=1000)
        resized = resize_image(img, max_width=1024)
        assert resized.shape[1] == 1024
        assert resized.shape[0] == 512  # maintains aspect ratio

    def test_small_image_unchanged(self):
        """Test that images smaller than max_width are not resized."""
        img = _make_test_image(width=200, height=100)
        resized = resize_image(img, max_width=1024)
        assert resized.shape[1] == 200


class TestDenoise:
    def test_output_same_shape(self):
        """Test that denoising preserves image dimensions."""
        img = _make_grayscale_image()
        denoised = denoise(img)
        assert denoised.shape == img.shape


class TestApplyThreshold:
    def test_binary_output(self):
        """Test that thresholding produces a binary image."""
        img = _make_grayscale_image()
        binary = apply_threshold(img)
        unique_values = np.unique(binary)
        assert all(v in [0, 255] for v in unique_values)


class TestSharpen:
    def test_output_same_shape(self):
        """Test that sharpening preserves image dimensions."""
        img = _make_grayscale_image()
        sharpened = sharpen(img)
        assert sharpened.shape == img.shape


class TestDeskew:
    def test_no_crash_on_simple_image(self):
        """Test that deskew doesn't crash on a simple image."""
        img = _make_grayscale_image()
        result = deskew(img)
        assert result.shape == img.shape

    def test_handles_empty_image(self):
        """Test deskew with a black (empty) image."""
        img = np.zeros((100, 200), dtype=np.uint8)
        result = deskew(img)
        assert result.shape == img.shape


class TestEncodeImage:
    def test_encode_to_png(self):
        """Test encoding numpy array to PNG bytes."""
        img = _make_grayscale_image()
        encoded = encode_image(img, ".png")
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_to_jpg(self):
        """Test encoding numpy array to JPEG bytes."""
        img = _make_grayscale_image()
        encoded = encode_image(img, ".jpg")
        assert isinstance(encoded, bytes)


class TestPreprocessPipeline:
    def test_full_pipeline_success(self):
        """Test the full preprocessing pipeline with a valid image."""
        import cv2
        img = _make_test_image()
        _, buffer = cv2.imencode(".png", img)
        result = preprocess_image(buffer.tobytes())

        assert result["success"] is True
        assert result["processed_image"] is not None
        assert isinstance(result["processed_bytes"], bytes)
        assert len(result["steps"]) >= 5
        assert "decoded" in result["steps"]
        assert "grayscale" in result["steps"]
        assert "thresholded" in result["steps"]

    def test_pipeline_with_invalid_image(self):
        """Test pipeline handles invalid image gracefully."""
        result = preprocess_image(b"not valid image data")
        assert result["success"] is False
        assert "decode_failed" in result["steps"]

    def test_pipeline_returns_original_size(self):
        """Test that original dimensions are reported."""
        import cv2
        img = _make_test_image(width=640, height=480)
        _, buffer = cv2.imencode(".png", img)
        result = preprocess_image(buffer.tobytes())

        assert result["original_size"] == (640, 480)
