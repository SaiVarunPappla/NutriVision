# NutriVision – System Planning Document

## Project Title
**NutriVision – AI-Based Ingredient Analysis System**

## Short Summary
NutriVision is an Android-based AI application that analyzes food ingredients from images or text inputs to provide detailed nutritional insights. The system uses computer vision and natural language processing techniques to identify ingredients, evaluate calorie and nutrient content, detect allergens, and determine dietary suitability. It helps users make informed and healthier food choices through personalized recommendations and nutrition tracking.

---

## 1. Problem Statement

Modern consumers face significant challenges in understanding the nutritional content and safety of the food they consume. Food labels are often difficult to read, contain technical jargon, and require specialized knowledge to interpret correctly. Key problems include:

- **Unreadable food labels**: Small text, complex ingredient names, and dense formatting make labels hard to understand
- **Lack of nutritional awareness**: Most consumers cannot estimate calorie counts or nutrient breakdowns from ingredient lists
- **Hidden allergens**: Allergens are often listed under unfamiliar names (e.g., "casein" for milk, "albumin" for eggs)
- **Dietary incompatibility**: Identifying whether a product suits vegetarian, vegan, gluten-free, or keto diets requires checking every ingredient
- **No personalized guidance**: Existing nutrition apps provide generic data without considering individual dietary needs and allergies
- **Time-consuming manual research**: Looking up each ingredient individually is impractical for daily food choices

NutriVision addresses these challenges by providing instant, AI-powered ingredient analysis that converts complex food label text into actionable nutritional insights.

---

## 2. Objectives

1. Develop an Android application that can analyze food ingredients from images or text inputs
2. Implement computer vision (OpenCV) and OCR (Tesseract) to extract ingredient text from food label images
3. Use NLP techniques to parse, clean, and normalize ingredient names
4. Integrate with USDA FoodData Central API for accurate nutritional data
5. Detect common food allergens using a rule-based classification system
6. Evaluate dietary suitability (vegetarian, vegan, gluten-free, dairy-free, keto)
7. Generate personalized health recommendations based on user profiles
8. Provide nutrition tracking through scan history
9. Deploy a modular FastAPI backend for scalable API services
10. Create a practical, demo-ready academic prototype

---

## 3. Scope

### In Scope
- Android mobile application (Kotlin + XML + Material Design)
- FastAPI backend with REST APIs
- Image-based ingredient extraction (camera/gallery → OCR)
- Text-based ingredient analysis (manual input)
- Nutrition lookup via USDA FoodData Central API
- Allergen detection (Big 14 allergens)
- Dietary suitability analysis (6 diet types)
- Personalized recommendations
- Scan history and nutrition tracking
- Firebase Firestore for data storage
- Demo mode for offline/presentation use

### Out of Scope
- Real-time barcode/QR code scanning
- Multi-language OCR support
- Meal planning and recipe generation
- Social features and sharing
- iOS/Web versions
- Integration with wearable devices
- Production-scale deployment

---

## 4. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | User can register and login using email/password | High |
| FR-02 | User can capture food label images using camera | High |
| FR-03 | User can upload food label images from gallery | High |
| FR-04 | User can enter ingredient text manually | High |
| FR-05 | System extracts text from images using OCR | High |
| FR-06 | System parses and normalizes ingredient names | High |
| FR-07 | System retrieves nutrition data from USDA API | High |
| FR-08 | System detects common allergens in ingredients | High |
| FR-09 | System evaluates dietary suitability | Medium |
| FR-10 | System generates health recommendations | Medium |
| FR-11 | System calculates overall health score | Medium |
| FR-12 | User can view scan history | Medium |
| FR-13 | User can set dietary preferences and allergies | Medium |
| FR-14 | User receives personalized allergen alerts | Medium |
| FR-15 | User can delete scan history entries | Low |

---

## 5. Non-Functional Requirements

| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-01 | Response time for text analysis | < 5 seconds |
| NFR-02 | Response time for image analysis | < 10 seconds |
| NFR-03 | OCR accuracy on clear label images | > 85% |
| NFR-04 | API availability | 99% uptime (development) |
| NFR-05 | App size | < 50 MB |
| NFR-06 | Supported Android versions | API 24+ (Android 7.0+) |
| NFR-07 | Concurrent users (prototype) | Up to 10 |
| NFR-08 | Data storage | Firebase free tier (1 GB) |
| NFR-09 | API rate limits | USDA: 1000 req/hour |
| NFR-10 | Security | Firebase Auth + HTTPS |

---

## 6. Use Cases

### UC-01: Analyze Food Image
- **Actor**: User
- **Precondition**: User is logged in
- **Steps**:
  1. User opens the scan screen
  2. User captures a photo of a food label or selects from gallery
  3. System preprocesses the image (OpenCV)
  4. System extracts text via OCR (Tesseract)
  5. System parses ingredients (NLP)
  6. System looks up nutrition data (USDA API)
  7. System detects allergens and checks dietary suitability
  8. System displays results with recommendations
- **Postcondition**: Scan saved to history

### UC-02: Analyze Text Input
- **Actor**: User
- **Precondition**: User is logged in
- **Steps**:
  1. User opens the text input screen
  2. User types or pastes ingredient list
  3. System parses and normalizes ingredients
  4. System looks up nutrition data
  5. System displays analysis results
- **Postcondition**: Scan saved to history

### UC-03: View Scan History
- **Actor**: User
- **Steps**:
  1. User navigates to history screen
  2. System retrieves past scans from Firestore
  3. User can view details of any past scan

### UC-04: Update Dietary Profile
- **Actor**: User
- **Steps**:
  1. User opens profile/settings
  2. User selects dietary preferences and allergies
  3. System saves preferences to Firestore
  4. Future scans use preferences for personalized alerts

---

## 7. User Roles

| Role | Description | Permissions |
|------|-------------|------------|
| **User** | Primary app user | Register, login, scan images/text, view results, view history, manage profile |
| **Demo User** | For viva/presentation | Access all features with demo data, no Firebase required |

---

## 8. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ANDROID APP (Kotlin)                       │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌───────┐  ┌───────────┐   │
│  │Splash│→ │Login │→ │Home  │→ │Scan   │→ │Result     │   │
│  └──────┘  └──────┘  └──────┘  └───────┘  └───────────┘   │
│                         │          │                         │
│                    ┌────┘    ┌─────┘                         │
│                    ▼         ▼                               │
│              ┌─────────┐  ┌──────────┐                      │
│              │History  │  │Profile   │                      │
│              └─────────┘  └──────────┘                      │
│                                                              │
│  [Retrofit HTTP Client] ←→ [Firebase Auth]                  │
└──────────────┬───────────────────────────────────────────────┘
               │ REST API (JSON)
               ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND (Python)                     │
│                                                              │
│  ┌─────────────────────────────────────────────┐            │
│  │              API Routes Layer                │            │
│  │  /scan/image  /scan/text  /nutrition         │            │
│  │  /history     /user       /health            │            │
│  └─────────────────┬───────────────────────────┘            │
│                    │                                         │
│  ┌─────────────────▼───────────────────────────┐            │
│  │            Service Layer                     │            │
│  │  OCR Service │ Nutrition │ Allergen │ Diet   │            │
│  │  Parser      │ Recommend │ Firestore         │            │
│  └─────────────────┬───────────────────────────┘            │
│                    │                                         │
│  ┌─────────────────▼───────────────────────────┐            │
│  │           AI/ML Pipeline                     │            │
│  │  OpenCV → Tesseract OCR → NLP Processor     │            │
│  │  TFLite Classifier (optional)               │            │
│  └─────────────────────────────────────────────┘            │
└──────────┬──────────────────────┬────────────────────────────┘
           │                      │
           ▼                      ▼
┌──────────────────┐   ┌─────────────────────┐
│  USDA FoodData   │   │  Firebase Firestore  │
│  Central API     │   │  (users, scans,      │
│  (Free)          │   │   results, history)  │
└──────────────────┘   └─────────────────────┘
```

---

## 9. Data Flow Diagram

### Level 0 (Context Diagram)
```
                    ┌─────────┐
  Food Image/Text → │         │ → Nutrition Analysis
                    │NutriVision│
  User Profile    → │         │ → Recommendations
                    └─────────┘
                         │
                    ┌────┘
                    ▼
              USDA API + Firestore
```

### Level 1 (System Processes)
```
User Input ──► [P1: Image Preprocessing] ──► Preprocessed Image
                                              │
Preprocessed Image ──► [P2: OCR Extraction] ──► Raw Text
                                                 │
Raw Text ──► [P3: NLP Parsing] ──► Ingredient List
                                    │
Ingredient List ──► [P4: Nutrition Lookup] ──► Nutrition Data
                                                │
Nutrition Data ──► [P5: Allergen Detection] ──► Allergens
                                                 │
Nutrition + Allergens ──► [P6: Diet Analysis] ──► Suitability
                                                   │
All Data ──► [P7: Recommendations] ──► Health Advice
                                        │
All Results ──► [P8: Storage] ──► Firestore
```

---

## 10. Module Breakdown

### Module 1: User Management
- Firebase Authentication (email/password)
- User profile CRUD in Firestore
- Dietary preference and allergy storage

### Module 2: Image Analysis Pipeline
- Camera capture / gallery selection (Android)
- Image upload to backend
- OpenCV preprocessing (grayscale, threshold, denoise, deskew, sharpen)
- Tesseract OCR text extraction

### Module 3: Text Analysis Pipeline
- Manual ingredient text input (Android)
- NLP section detection (find "Ingredients:" header)
- Ingredient splitting (comma/semicolon/newline)
- Per-ingredient cleaning (remove %, quantities, E-numbers, noise)
- Normalization (map variant names to standard names)
- Deduplication

### Module 4: Nutrition Lookup
- USDA FoodData Central API integration (primary)
- Edamam API abstraction (optional/pluggable)
- Per-ingredient nutrition retrieval
- Total nutrition aggregation
- Daily value percentage computation

### Module 5: Allergen Detection
- Rule-based allergen identification (14 categories)
- Keyword matching against allergen database
- User-specific allergen alerting
- Separate allergen warning text extraction

### Module 6: Dietary Suitability
- Rule-based diet classification
- Vegetarian / Vegan / Gluten-free / Dairy-free / Keto / Nut-free
- Ingredient-to-diet mapping

### Module 7: Recommendations
- Health score calculation (0-10)
- Nutritional warnings (high sodium, sugar, saturated fat)
- Personalized suggestions based on user profile
- Allergen-specific alerts

### Module 8: History & Tracking
- Scan history storage in Firestore
- History listing with summary data
- Scan detail retrieval
- History deletion

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Platform | Android |
| Frontend | Kotlin, XML, Material Design |
| Backend | Python (FastAPI) |
| AI/ML | TensorFlow Lite, OpenCV, NLP |
| Database | Firebase Firestore |
| APIs | USDA FoodData Central / Edamam API |
| Tools | Android Studio, Git, Postman |
