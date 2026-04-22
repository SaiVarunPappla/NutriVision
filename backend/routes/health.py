"""
NutriVision - Health Check Route

Provides a simple health check endpoint to verify the API is running,
Firebase connectivity, and external API availability.
"""

from fastapi import APIRouter
from config import settings
from firebase_config import is_firebase_available

router = APIRouter()


@router.get("/health", summary="Health Check")
async def health_check():
    """
    Returns the health status of the NutriVision API.

    Checks:
    - API server status
    - Firebase/Firestore connectivity
    - USDA API key configuration
    - Edamam API configuration (optional)
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "services": {
            "api": "running",
            "firebase": "connected" if is_firebase_available() else "demo_mode",
            "usda_api": "configured" if settings.usda_api_key != "DEMO_KEY" else "demo_key",
            "edamam_api": "configured" if settings.is_edamam_configured else "not_configured",
        },
        "debug": settings.debug,
    }


@router.get("/", summary="Root")
async def root():
    """Root endpoint - redirects to API docs."""
    return {
        "message": "Welcome to NutriVision API",
        "description": (
            "AI-Based Ingredient Analysis System. "
            "Visit /docs for interactive API documentation."
        ),
        "version": settings.app_version,
        "docs_url": "/docs",
    }
