"""
NutriVision - Scan Endpoint Tests

Tests for POST /api/v1/scan/text and POST /api/v1/scan/image endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test that the health endpoint returns a healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "NutriVision"


def test_root_endpoint():
    """Test the root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "NutriVision" in data["message"]


def test_scan_text_success():
    """Test text-based ingredient scanning with valid input."""
    response = client.post("/api/v1/scan/text", json={
        "text": "sugar, flour, butter, salt",
        "user_id": "test_user_001",
        "product_name": "Test Cookies"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["scan_type"] == "text"
    assert data["product_name"] == "Test Cookies"
    assert len(data["ingredients"]) == 4
    assert data["ingredients"][0]["normalized_name"] == "sugar"


def test_scan_text_empty():
    """Test text scanning with empty text raises validation error."""
    response = client.post("/api/v1/scan/text", json={
        "text": "",
        "user_id": "test_user_001",
    })
    assert response.status_code == 422  # Validation error (min_length=2)


def test_scan_text_missing_user_id():
    """Test text scanning without user_id raises validation error."""
    response = client.post("/api/v1/scan/text", json={
        "text": "sugar, flour",
    })
    assert response.status_code == 422


def test_get_scan_not_found():
    """Test retrieving a non-existent scan returns 404."""
    response = client.get("/api/v1/scan/nonexistent_id")
    assert response.status_code == 404


def test_scan_response_structure():
    """Test that scan response contains all required fields."""
    response = client.post("/api/v1/scan/text", json={
        "text": "rice, chicken, onion",
        "user_id": "test_user_001",
    })
    data = response.json()

    # Verify all expected top-level keys present
    expected_keys = [
        "scan_id", "status", "scan_type", "extracted_text",
        "ingredients", "nutrition", "allergens",
        "dietary_suitability", "health_score", "recommendations"
    ]
    for key in expected_keys:
        assert key in data, f"Missing key: {key}"
