"""
NutriVision – AI-Based Ingredient Analysis System
==================================================

FastAPI Backend Entry Point

This server provides REST APIs for:
- Image-based ingredient analysis (OCR + AI)
- Text-based ingredient analysis (NLP)
- Nutrition lookup via USDA FoodData Central
- Allergen detection and dietary suitability
- Personalized recommendations
- User management and scan history

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Swagger docs available at:
    http://localhost:8000/docs
"""
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI()

class AnalysisRequest(BaseModel):
    ingredients: str

@app.post("/api/v1/analyze")
async def analyze(request: AnalysisRequest):
    # 1. Use Spoonacular/OpenFoodFacts here
    # 2. Use your API keys from os.getenv("SPOONACULAR_KEY")
    # 3. Return results
    return {"status": "success", "data": f"Analyzed: {request.ingredients}"}

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from firebase_config import initialize_firebase

# Import route modules
from routes.health import router as health_router
from routes.scan import router as scan_router
from routes.nutrition import router as nutrition_router
from routes.history import router as history_router
from routes.user import router as user_router
from routes.chat import router as chat_router
import requests
import os

from utils.sanitizer import sanitize_ingredient

def get_nutritional_info(ingredient):
    clean_ingredient = sanitize_ingredient(ingredient)
    if not clean_ingredient:
        return {"error": "Invalid ingredient"}
    
    api_key = os.getenv("SPOONACULAR_API_KEY")
    url = f"https://api.spoonacular.com/food/ingredients/search?query={clean_ingredient}&apiKey={api_key}"
    response = requests.get(url)
    return response.json()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for the FastAPI app."""
    # --- Startup ---
    print(f"[NutriVision] Starting {settings.app_name} v{settings.app_version}")
    initialize_firebase()
    print(f"[NutriVision] USDA API configured: {bool(settings.usda_api_key)}")
    print(f"[NutriVision] Edamam API configured: {settings.is_edamam_configured}")
    print(f"[NutriVision] Server ready at http://{settings.host}:{settings.port}")
    print(f"[NutriVision] Swagger docs at http://{settings.host}:{settings.port}/docs")

    yield

    # --- Shutdown ---
    print("[NutriVision] Shutting down...")


app = FastAPI(
    title="NutriVision API",
    description=(
        "**NutriVision – AI-Based Ingredient Analysis System**\n\n"
        "NutriVision is an Android-based AI application that analyzes food "
        "ingredients from images or text inputs to provide detailed nutritional "
        "insights. The system uses computer vision and natural language processing "
        "techniques to identify ingredients, evaluate calorie and nutrient content, "
        "detect allergens, and determine dietary suitability.\n\n"
        "**Tech Stack:** Python (FastAPI) · TensorFlow Lite · OpenCV · NLP · "
        "Firebase Firestore · USDA FoodData Central"
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register Routes ---
app.include_router(health_router, tags=["Health"])
app.include_router(scan_router, prefix="/api/v1", tags=["Scan"])
app.include_router(nutrition_router, prefix="/api/v1", tags=["Nutrition"])
app.include_router(history_router, prefix="/api/v1", tags=["History"])
app.include_router(user_router, prefix="/api/v1", tags=["User"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
