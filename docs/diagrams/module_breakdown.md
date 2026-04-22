# NutriVision – Module Breakdown

## Module Architecture

```mermaid
graph TB
    subgraph "Module 1: User Management"
        M1A["Firebase Auth"]
        M1B["User Profile CRUD"]
        M1C["Preferences Storage"]
    end

    subgraph "Module 2: Image Analysis"
        M2A["Camera/Gallery Capture"]
        M2B["OpenCV Preprocessing"]
        M2C["Tesseract OCR"]
    end

    subgraph "Module 3: Text Analysis"
        M3A["Text Input"]
        M3B["NLP Section Detection"]
        M3C["Ingredient Parser"]
        M3D["Name Normalization"]
    end

    subgraph "Module 4: Nutrition Lookup"
        M4A["USDA API Client"]
        M4B["Edamam Client (Optional)"]
        M4C["Nutrition Calculator"]
    end

    subgraph "Module 5: Allergen Detection"
        M5A["Allergen Database"]
        M5B["Keyword Matcher"]
        M5C["User Alert Generator"]
    end

    subgraph "Module 6: Diet Suitability"
        M6A["Diet Rule Engine"]
        M6B["Ingredient Classifier"]
    end

    subgraph "Module 7: Recommendations"
        M7A["Health Scorer"]
        M7B["Warning Generator"]
        M7C["Suggestion Engine"]
    end

    subgraph "Module 8: History"
        M8A["Scan Storage"]
        M8B["History Retrieval"]
    end

    M2A --> M2B --> M2C --> M3C
    M3A --> M3B --> M3C --> M3D
    M3D --> M4A & M4B
    M4A & M4B --> M4C
    M4C --> M5A --> M5B
    M5B --> M6A --> M6B
    M6B --> M7A --> M7B --> M7C
    M7C --> M8A
    M1C --> M5C & M7C
```

## Module File Mapping

| Module | Backend Files | Android Files (Phase 5-6) |
|--------|--------------|--------------------------|
| M1: User Management | `routes/user.py`, `services/firestore_service.py`, `models/user.py` | `ui/auth/`, `data/repository/UserRepository.kt` |
| M2: Image Analysis | `ml/image_preprocessor.py`, `ml/ocr_engine.py`, `services/ocr_service.py` | `ui/scan/ImageScanFragment.kt`, `utils/ImageUtils.kt` |
| M3: Text Analysis | `ml/nlp_processor.py`, `services/ingredient_parser.py` | `ui/scan/TextInputFragment.kt` |
| M4: Nutrition Lookup | `integrations/usda_api.py`, `integrations/edamam_api.py`, `services/nutrition_service.py` | — |
| M5: Allergen Detection | `services/allergen_service.py`, `utils/constants.py` | — |
| M6: Diet Suitability | `services/diet_service.py`, `utils/constants.py` | — |
| M7: Recommendations | `services/recommendation_service.py`, `models/recommendation.py` | `ui/result/ResultFragment.kt` |
| M8: History | `routes/history.py`, `services/firestore_service.py` | `ui/history/HistoryFragment.kt` |
