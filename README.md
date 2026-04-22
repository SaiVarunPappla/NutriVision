# NutriVision
NutriVision is an Android-based AI application that analyzes food ingredients from images or text inputs to provide detailed nutritional insights, NutriVision is an AI-powered food analysis mobile application that helps users understand packaged food products using image scan, OCR, ingredient analysis, nutrition insights, allergen checks, dietary suitability detection, and context-aware AI assistance.

It is designed as a final-year engineering project focused on improving food awareness through mobile technology, backend intelligence, and user-friendly health-tech design.

---

## Features

- Image-based food label scanning
- OCR-based text extraction from packaged food labels
- Product-name normalization and branded product lookup
- Ingredient-level nutrition fallback when branded match is uncertain
- Nutrition summary and health score generation
- Allergen detection
- Dietary suitability analysis
- AI chatbot for scan-based and general nutrition questions
- Authentication with email/password and phone OTP
- Scan history tracking
- Modern Android UI with Material-based design

---

## Project Structure

```text
NutriVision/
├── android/                # Android application
│   └── NutriVision/
├── backend/                # FastAPI backend services
├── README.md
└── .gitignore
```

---

## Tech Stack

### Android
- Kotlin
- XML
- Android Studio
- Material Design / Material 3 components
- Navigation Component
- RecyclerView
- ViewModel / LiveData
- Camera / image selection integration

### Backend
- Python
- FastAPI
- Uvicorn
- OCR + normalization services
- Nutrition and product lookup integrations
- AI prompt orchestration for scan and chat flows

### Services / Concepts
- OCR-based label extraction
- Product name resolver
- Confidence-gated branded lookup
- Ingredient-level fallback analysis
- Personalized AI response behavior
- Firebase/Auth-related mobile flow integration

---

## Core Workflow

1. User scans a packaged food label or enters ingredients manually.
2. OCR extracts visible text from the product label.
3. Product resolver normalizes the likely visible product name.
4. If confidence is high, the backend tries branded product lookup.
5. If confidence is low, the system skips branded lookup and performs ingredient-level analysis.
6. The app shows:
   - product name,
   - confidence/trust indicator,
   - health score,
   - nutrition overview,
   - ingredients,
   - allergens,
   - dietary suitability,
   - recommendations.
7. NutriVision AI can then answer:
   - scan-grounded questions,
   - ingredient explanation questions,
   - general nutrition and health-awareness questions.

---

## Key Highlights

### Confidence-Gated Product Matching
NutriVision avoids blindly trusting OCR-derived product names.  
If product-name confidence is low, branded lookup is skipped and ingredient-level fallback is used instead. This reduces incorrect product matches.

### Grounded AI Responses
The chatbot is designed to answer using scan context when available, and to act like a general educational nutrition assistant when scan context is missing.

### Mobile-First Health-Tech UX
The app emphasizes clear trust messaging, confidence badges, section cards, and user-friendly AI chat for real-world food awareness use.

---

## Authentication

The app currently supports:
- Email/password login
- Phone OTP login

Google Sign-In may be incomplete or not fully working in the current version.

---

## Running the Project

## 1. Clone the repository

```bash
git clone https://github.com/SaiVarunPappla/NutriVision.git
cd NutriVision
```

## 2. Backend setup

Open terminal in the `backend` folder:

```bash
cd backend
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backend:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 3. Android setup

Open only this folder in Android Studio:

```text
android/NutriVision
```

Let Gradle sync complete.

Connect a physical Android device with USB debugging enabled.

Run:

```bash
adb devices
```

If using a physical device for local backend access, run:

```bash
adb reverse tcp:8000 tcp:8000
```

Then click **Run** in Android Studio.

---

## Physical Device Setup

For Samsung devices:
1. Turn off Auto Blocker if USB debugging is restricted.
2. Enable Developer Options by tapping Build Number multiple times.
3. Turn on USB Debugging.
4. Connect the phone using a proper USB data cable.
5. Choose **Transferring files** mode.
6. Accept the USB debugging authorization popup.

---

## Environment Variables

Sensitive files such as `.env` are **not included** in the repository.

Create your own environment file in the backend folder and provide the required API keys and configuration values.

Example:

```env
API_KEY_EXAMPLE=your_key_here
ANOTHER_SECRET=your_value_here
```

You can also create a `.env.example` file for contributors without exposing real secrets.

---

## Current Limitations

- Google Sign-In is not fully working in the current version.
- OCR quality depends on image clarity, lighting, and label visibility.
- Some products may fall back to ingredient-level analysis when branded matching is uncertain.
- External nutrition/product APIs may affect result availability and consistency.

---

## Screens / Modules

- Login / Register
- Phone OTP Login
- Home
- Image Scan
- Text Input
- Result Screen
- AI Chat
- History
- Profile

---

## Future Improvements

- Better scan preprocessing for improved OCR quality
- Stronger personalized AI using user profile context
- More robust product matching across multiple nutrition/product databases
- Improved offline caching and result persistence
- Expanded dietary recommendation logic
- Better Google authentication support
- Production deployment and analytics

---

## Demo Credentials

Use only for testing in the current development/demo setup.

### Email Login
- Email: `xxxxxx@gmail.com`
- Password: `xxxxx4`

### Phone OTP
- Number: `10-digit number`
- OTP: `set your otp in firebase`

### Alternate Phone OTP
- Number: `10-digit number`
- OTP: `set your otp in firebase`

---

## Author

**Sai Varun Pappla**

## Disclaimer

NutriVision is an educational and informational application.  
It is not a medical diagnosis or treatment tool. Users should consult qualified professionals for medical advice.
