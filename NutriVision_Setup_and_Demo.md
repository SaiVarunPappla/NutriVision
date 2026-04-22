# NutriVision – Setup & Demo Guide

## System Deployment Overview
This system operates in two core phases requiring separate active instances locally interacting securely. It's expressly designed enabling offline `Demo Mode` capabilities mapping effectively guaranteeing academic presentation stability.

---

## 1. Backend Service Configuration (FastAPI)

Ensure standard dependencies are resolved:
```bash
cd backend/
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Starting the Server
Start the Uvicorn engine natively wrapping port 8000 channels.
```bash
uvicorn main:app --port 8000
```
*Note: If `TESSERACT_CMD` or external API keys are missing inside `.env`, the server handles initialization successfully falling backwards directly entering "Demo Mode" dynamically routing internal local variables safely preserving presentation integrity.* 

---

## 2. Android Client Compilation (Kotlin/Native)

### Understanding Target Networking (Using `10.0.2.2`)
The project utilizes `Retrofit` handling REST APIs safely. While standard applications operate alongside `localhost` configurations, Android Emulators physically isolate sandboxed IP configurations specifically rendering standard localhost bindings isolated inwards explicitly pointing at entirely unassociated Android internal nodes natively. 
**Solution:** The system dynamically points the base target explicitly towards `http://10.0.2.2:8000/api/` representing the host machines actual localhost IP safely. 

### Allowing Cleartext Contexts (Local Development)
Because Uvicorn explicitly initializes an `HTTP` endpoint routing rather than HTTPS, standard Android environments immediately block traffic generating SSL/Security Exceptions.
- We specifically overrode `AndroidManifest.xml` targeting `android:usesCleartextTraffic="true"` strictly deployed for local development flows seamlessly allowing Demo tests cleanly. 

### Executing the Emulator
1. Open the project recursively mapping `android/NutriVision/` utilizing **Android Studio**.
2. Wait for background Gradle `assembleDebug` tasks syncing completely smoothly resolving Kotlin syntax references internally. 
3. Execute the `Run 'app'` command natively tracking towards a Nougat/API 24+ emulator locally. 

---

## 3. Recommended Demo Flow Walkthrough

Once both systems execute actively, follow these strict demonstration protocols ensuring fluid presentations highlighting core systemic constraints reliably:

1. **Onboarding Authentication:**
   - Launch application waiting for the 2.0s standard Mock Splash boot.
   - Interact via standard string mocks routing straight into the **Home Dashboard**. 
2. **Text Scanning Evaluation:**
   - Click **Input Ingredients**. 
   - Ensure the server logs execute visually alongside the Android App. Type exact string definitions identifying allergens (ex: "Peanuts, Soy Lecithin, enriched white flour").
   - Click "Analyze". 
   - Highlight the `<ProgressBar>` confirming asynchronous background rendering properly awaiting Uvicorn's `200 OK` JSON payloads structurally decoding back. 
   - Identify the exact red visual cues correctly flagging `Allergen Dangers`. 
3. **Capture Simulation:**
   - Backtrack towards Home Dashboard clicking **Scan Food Label**. 
   - Highlight the Camera capture placeholder framing logic smoothly pressing Capture binding multipart objects directly translating across backend interfaces gracefully displaying fallback offline mock interfaces if the camera logic hasn't parsed bytes actively. 
4. **History Presentation:**
   - Transition towards the bottom UI components clicking `History`. 
   - Identify Retrofit executing `GET /history/{user}` properly hydrating our `HistoryAdapter` mapping prior calculations dynamically confirming persistence interfaces. 
5. **Configuring Output Profile:**
   - Proceed towards `Profile`. 
   - Explicitly configure `Vegan` & `Vegetarian` preferences simulating standard UI triggers effectively mapping changes back targeting Uvicorn properly ensuring personalized endpoints configure successfully locally.
