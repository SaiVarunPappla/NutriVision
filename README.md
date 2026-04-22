# NutriVision

NutriVision is an Android + FastAPI health-tech project that helps users understand packaged foods from label text, scanned images, and ingredient lists.

It combines on-device OCR, nutrition-source aggregation, allergen detection, dietary checks, health scoring, and context-aware AI guidance in one mobile workflow.

---

## Problem It Solves

Packaged food labels are often difficult to interpret quickly, especially for users managing:

- allergies,
- diet preferences,
- weight goals,
- ingredient quality concerns,
- general nutrition awareness.

NutriVision turns raw label text into actionable guidance by helping answer:

- What this product likely is
- What key ingredients and nutrients matter
- Which allergens are present
- Whether it fits common diet preferences
- What practical next step the user should take

---

## Project Impact

These are engineering implementation metrics from the current codebase:

- **10 API endpoints** exposed across health, scan, user, history, nutrition, chat, and analyze flows
- **2 primary scan entry modes** in the Android app: image scan and manual text input
- **4 nutrition data source integrations** in the backend: USDA, OpenFoodFacts, API-Ninjas, and optional Edamam path
- **14 allergen categories** covered through rule-based detection mapping
- **6 dietary suitability checks**: vegetarian, vegan, gluten-free, dairy-free, keto-friendly, and nut-free
- **3 authentication methods** in Android flow: email/password, Google Sign-In path, and phone OTP
- **7 core user-facing fragments**: Home, Scan, Text Input, Result, Chat, History, and Profile
- Confidence-gated branded product matching with ingredient-level fallback when confidence is low

---

## Key Features

### Scan and Analysis
- Camera-based food label scan
- Gallery image import for scan analysis
- On-device OCR extraction via ML Kit
- Product name normalization before branded lookup
- Confidence threshold logic to avoid unsafe product-name assumptions
- Ingredient parsing and per-ingredient nutrition fallback analysis
- Nutrition summary with daily value percentages
- Health score calculation with warning and suggestion generation
- Allergen detection using rule-based ingredient matching
- Dietary suitability classification

### AI Guidance
- **Scan AI mode** when scan context is available
- **General AI mode** when scan context is not available
- Context-aware nutrition explanations
- Low-confidence clarification behavior
- User-profile-aware AI responses for diet preference and allergy sensitivity

### Mobile App Experience
- Authentication with email/password, Google Sign-In path, and phone OTP
- History module
- Profile module
- Result screen with confidence and trust cues
- Chat experience for both scan-based and general nutrition Q&A

---

## Real Architecture Overview

### Mobile (Android)
- Kotlin + XML app
- Single-activity navigation architecture
- CameraX + ML Kit text recognition for image scanning
- Retrofit + OkHttp for backend communication
- Shared ViewModel-based data passing between result and chat flows
- Firebase Authentication for login flows

### Backend (FastAPI)
- Route layer for scan, chat, user, history, nutrition, health, and analyze flows
- Service layer for OCR handling, ingredient parsing, nutrition lookup, allergen checks, dietary checks, recommendations, and chat prompt orchestration
- Integration layer for external nutrition providers
- Pydantic models for typed request and response contracts
- Firestore service abstraction with demo-style fallback behavior where full persistence is incomplete

---

## Core Workflow

1. User scans a label image or enters ingredient text manually.
2. Android extracts OCR text in the image flow, or sends manual text directly.
3. Backend optionally normalizes the visible product name from OCR.
4. Backend attempts branded lookup only when confidence is sufficient.
5. If branded confidence is low or no reliable match is found, backend falls back to ingredient-level nutrition analysis.
6. Backend computes:
   - nutrition summary,
   - allergens,
   - dietary suitability,
   - recommendations,
   - health score.
7. App shows the result screen with confidence and trust cues.
8. User can continue with AI chat for scan-grounded or general nutrition guidance.

---

## Scan Pipeline

### Image Path
- CameraX preview and capture in Android
- ML Kit text recognition on selected or captured image
- Upload recognized text to backend scan-text route
- Optional product-name candidate passed from the largest OCR text block

### Backend Decision Logic
- Branded lookup attempt for product-name candidates
- Confidence gate around trustworthy product matching
- If below threshold, branded trust path is skipped
- Ingredient parsing and multi-source nutrition fallback run next
- Allergen detection, dietary suitability, recommendation generation, and health scoring are applied afterward

### Server OCR Route
A backend image OCR route also exists, but the current Android flow primarily uses on-device OCR and posts extracted text through the text scan path.

---

## AI Chat Behavior

### Chat Endpoint
`POST /api/v1/chat`

### Current Behavior
- Accepts a user question
- Accepts optional `scan_context`
- Accepts optional `user_profile`
- Uses Gemini when configured
- Falls back to a safer local response style if Gemini is unavailable

### AI Safety Rules
- Does not invent product-specific facts
- Acknowledges uncertainty when confidence is low
- Avoids diagnosis, treatment, or medical certainty claims
- Prefers grounded answers when scan context exists

---

## Authentication Methods

The Android app currently includes:

- Email and Password login
- Google Sign-In flow path
- Phone OTP verification flow

> Note: Google Sign-In may still require additional polishing depending on local Firebase setup.

---

## API Endpoints

| Method | Endpoint | Purpose |
|-------|----------|---------|
| POST | `/api/v1/analyze` | Analyze nutrition/ingredient-related input |
| GET | `/health` | Health check route |
| POST | `/api/v1/scan/text` | Scan text analysis flow |
| POST | `/api/v1/scan/image` | Backend OCR image scan flow |
| GET | `/api/v1/scan/{scan_id}` | Retrieve scan details |
| POST | `/api/v1/chat` | AI chat endpoint |
| GET | `/api/v1/user/{user_id}` | Get user profile |
| PUT | `/api/v1/user/{user_id}` | Update user profile |
| GET | `/api/v1/history/{user_id}` | Get scan history |
| DELETE | `/api/v1/history/{history_id}` | Delete history item |
| GET | `/api/v1/nutrition/{scan_id}` | Get nutrition by scan ID |

### Notes
- History and nutrition retrieval routes still include TODO-style completion points.
- User routes may currently return mock-style profile data depending on implementation state.

---

## Tech Stack

### Android
- Kotlin
- XML layouts
- AndroidX Navigation
- ViewModel + LiveData
- RecyclerView
- Material components
- CameraX
- ML Kit Text Recognition
- Firebase Auth + Firestore SDK
- Retrofit + OkHttp + Gson

### Backend
- Python
- FastAPI
- Uvicorn
- Pydantic + pydantic-settings
- Requests + HTTPX
- OpenCV + Pillow + pytesseract
- Firebase Admin + Google Firestore client

---

## Folder Structure

```text
NutriVision/
├─ android/
│  └─ NutriVision/
│     ├─ app/
│     │  ├─ src/main/java/com/nutrivision/app/
│     │  └─ src/main/res/
│     ├─ build.gradle.kts
│     └─ settings.gradle.kts
├─ backend/
│  ├─ routes/
│  ├─ services/
│  ├─ integrations/
│  ├─ models/
│  ├─ ml/
│  ├─ utils/
│  ├─ tests/
│  ├─ main.py
│  ├─ config.py
│  └─ requirements.txt
├─ docs/
└─ README.md
```

---

## Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/SaiVarunPappla/NutriVision.git
cd NutriVision
```

---

### 2. Backend Setup

Open a terminal inside the `backend` folder:

```bash
cd backend
```

Create and activate a virtual environment:

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Install dependencies
```bash
pip install -r requirements.txt
```

Run the backend:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API docs:
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

---

### 3. Android Setup

1. Open **only** the Android project folder in Android Studio:

```text
android/NutriVision
```

2. Let Gradle sync complete.
3. Run the app on an emulator or physical device.

#### For Physical Device Testing
If using a real Android phone and local backend:

```bash
adb devices
adb reverse tcp:8000 tcp:8000
```

This allows the app on the phone to access the backend running on your laptop.

---

## Samsung Physical Device Notes

If testing on a Samsung phone:

1. Turn off **Auto Blocker** if USB debugging is restricted.
2. Enable **Developer Options** by tapping **Build Number** multiple times.
3. Turn on **USB Debugging**.
4. Connect the device using a proper USB data cable.
5. Set USB mode to **Transferring files**.
6. Accept the USB debugging authorization prompt.

---

## Environment Variables

Create a `.env` file for backend configuration.

> Do **not** commit real secrets to GitHub.

Example safe template:

```env
APP_NAME=NutriVision
APP_VERSION=1.0.0
DEBUG=true
HOST=0.0.0.0
PORT=8000

USDA_API_KEY=YOUR_USDA_KEY
USDA_BASE_URL=https://api.nal.usda.gov/fdc/v1

SPOONACULAR_API_KEY=YOUR_SPOONACULAR_KEY
SPOONACULAR_BASE_URL=https://api.spoonacular.com

OFF_USER=YOUR_OPENFOODFACTS_USER
OFF_PASS=YOUR_OPENFOODFACTS_PASS
OPENFOODFACTS_BASE_URL=https://world.openfoodfacts.net

EDAMAM_APP_ID=YOUR_EDAMAM_APP_ID
EDAMAM_APP_KEY=YOUR_EDAMAM_APP_KEY
EDAMAM_BASE_URL=https://api.edamam.com/api

API_NINJAS_API_KEY=YOUR_API_NINJAS_KEY
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json
FIREBASE_PROJECT_ID=YOUR_FIREBASE_PROJECT_ID

CORS_ORIGINS=*
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Recommended:
- keep real secrets only in local `.env`,
- add `.env` to `.gitignore`,
- optionally create a `.env.example` file with placeholders only.

---

## Current Limitations

- History route may currently return placeholder or incomplete data.
- Nutrition lookup by scan ID is not fully completed.
- User profile route may still return mock-style payloads depending on current backend implementation.
- Android scan flow primarily uses ML Kit OCR plus `/scan/text` rather than full multipart `/scan/image` upload.
- Retrofit base URL may still be hardcoded for local development in the current setup.
- Cleartext traffic is enabled for local development workflows.
- Some navigation references may still point to features under refinement.
- Google Sign-In may require additional project-side setup or cleanup.

---

## Future Improvements

- Full Firestore-backed history and nutrition retrieval
- Build-variant or environment-based Retrofit base URL configuration
- Complete Android multipart image upload flow for `/scan/image`
- Stronger production authentication hardening
- Improved Google Sign-In stability
- Local offline caching of history and results
- Better OCR confidence analytics and retake guidance
- CI checks for endpoint contracts and route coverage
- Expanded AI personalization using richer user-profile context

---

## Demo and Testing Credentials

Use **safe sample placeholders only** in public documentation.

### Sample Email Login
- Email: `demo-user@example.com`
- Password: `ChangeMe123`

### Sample Phone OTP
- Number: `+10000000000`
- OTP: configure in Firebase test setup

> Do not publish real personal credentials in a public README.

---

## Why This Project Matters

NutriVision is more than a label scanner. It is a mobile-first food-awareness system that combines computer vision, backend nutrition intelligence, and cautious AI guidance to help users make better food decisions faster.

It is especially useful for:
- people checking allergens,
- users comparing processed food quality,
- users following common diet styles,
- students and researchers exploring applied AI in health-tech,
- developers building OCR + nutrition-analysis pipelines.

---

## Disclaimer

NutriVision is an educational and informational project for food awareness.

It is **not** a medical diagnosis, treatment, prescription, or emergency guidance tool.

For medical decisions, allergy risk management, or treatment-related questions, consult qualified healthcare professionals.

---

## Author

**Sai Varun Pappla**
