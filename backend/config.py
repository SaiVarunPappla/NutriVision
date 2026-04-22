"""
NutriVision Backend - Application Configuration

Loads settings from environment variables (.env file).
Uses pydantic-settings for type-safe configuration.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        extra='ignore'
    )

    # --- App ---
    app_name: str = "NutriVision"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # --- USDA FoodData Central (Primary API) ---
    usda_api_key: str = "DEMO_KEY"
    usda_base_url: str = "https://api.nal.usda.gov/fdc/v1"

    # --- API-Ninjas (Nutrition API) ---
    api_ninjas_api_key: Optional[str] = None
    api_ninjas_base_url: str = "https://api.api-ninjas.com/v1"

    # --- OpenFoodFacts (Secondary API) ---
    openfoodfacts_base_url: str = "https://world.openfoodfacts.org"

    # --- Edamam API (Optional) ---
    edamam_app_id: Optional[str] = None
    edamam_app_key: Optional[str] = None
    edamam_base_url: str = "https://api.edamam.com/api"

    # --- Gemini API (Optional) ---
    gemini_api_key: Optional[str] = None

    # --- Firebase ---
    firebase_credentials_path: str = "firebase-service-account.json"
    firebase_project_id: str = ""

    # --- CORS ---
    cors_origins: str = "*"

    # --- Tesseract OCR ---
    tesseract_cmd: Optional[str] = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_edamam_configured(self) -> bool:
        """Check if Edamam API credentials are provided."""
        return bool(self.edamam_app_id and self.edamam_app_key)

    @property
    def is_api_ninjas_configured(self) -> bool:
        return bool(self.api_ninjas_api_key)


# Singleton settings instance
settings = Settings()