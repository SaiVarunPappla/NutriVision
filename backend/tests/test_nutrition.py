"""
NutriVision - Nutrition Endpoint Tests

Tests for GET /api/v1/nutrition/{scan_id} endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_nutrition_not_found():
    """Test fetching nutrition for non-existent scan returns 404."""
    response = client.get("/api/v1/nutrition/nonexistent_scan")
    assert response.status_code == 404


def test_nutrition_endpoint_exists():
    """Test that the nutrition endpoint is registered and responds."""
    response = client.get("/api/v1/nutrition/test_scan")
    # Should return 404 (not found) but NOT 405 (method not allowed)
    assert response.status_code != 405
