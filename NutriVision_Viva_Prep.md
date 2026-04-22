# NutriVision – Viva Preparation & Q&A

## Academic Viva Questions

**Q1: Why did you choose FastAPI over traditional frameworks like Django or Flask?**
**A1:** FastAPI offers massive asynchronous I/O advantages explicitly suited for rapid machine learning models and high-volume external REST calls (e.g. querying the USDA database). It relies heavily on standard Pydantic schema validation mapping out our complex data models naturally translating inwards generating Swagger Documentation concurrently allowing our Frontend to map easily natively. Standard Django structures rely inherently upon relational mechanisms which felt bloated considering our strict NoSQL Firebase Firestore architectural design.

**Q2: How do you bypass Localhost constraints navigating Traffic within the Android Emulator?**
**A2:** Android Emulators natively block targeting `localhost:8000` because the virtualized container treats "localhost" dynamically associating mapping directly to its internal self-confined network loops instead of the host machine compiling the server. We bypass this constraint forcefully utilizing `10.0.2.2:8000` executing physical proxy tunnels referencing the true host machine safely. 

**Q3: How exactly does the application operate "Offline"? Discuss the architecture behind the "Demo Mode"?**
**A3:** Standard integrations inherently collapse if specific 3rd party architectures timeout (e.g. USDA servers throttling/Firebase constraints/Network timeouts). Our Python integration is completely padded operating a fallback singleton explicitly isolating failed configuration dependencies mapping internal "Mock Templates." Instead of terminating, the system generates synthesized exact replicas (example: extracting *Soy Lecithin* maps dynamically generating health-scores identically validating internal logic parsing independently of database validations preserving all presentation integrity inherently).

**Q4: Can you explain your OCR architecture? Why PyTesseract and OpenCV?**
**A4:** Raw packaging is heavily distorted. Tesseract cannot translate curved plastic inherently. We engineered a specific OpenCV module applying standard adaptive Grayscale masking, generating binary thresholding techniques mapping the image purely capturing extreme structural contrast differences. This cleans the geometric inputs mapping straight vectors safely translating words into strings preventing excessive algorithmic garbage parsing perfectly complementing standard PyTesseract evaluations.

**Q5: What are the security vulnerabilities associated with `UsesCleartextTraffic=True`?**
**A5:** Adding `UsesCleartextTraffic=True` into `AndroidManifest.xml` explicitly bypasses standard Android enforcing strictly parsed HTTPS protocol configurations across external calls allowing natively insecure TCP port connections exposing traffic unencrypted perfectly easily allowing Man-In-The-Middle attacks realistically. We explicitly configure this natively guaranteeing local development `HTTP` flows remain functioning efficiently without configuring complex SSL tunneling architectures just to debug algorithms successfully.

**Q6: What is the benefit of single-activity architecture coupled alongside the Navigation component?**
**A6:** It prevents massive heap bloat. Instead of generating physical Android `Activities` dynamically stacking massive contextual footprints mapping every single screen, our NavHost effectively orchestrates localized Fragment views seamlessly swapping components securely enforcing `popUpTo` interactions reliably ensuring minimal RAM impact and lightning fast programmatic swaps without rebuilding entire application frames physically.

**Q7: Explain the NLP Algorithm structuring the ingredient groupings.**
**A7:** Ingredients arrive wildly mismanaged (ex. "LESS THAN 2% ENRICHED WHEAT FLOUR (NIACIN, RIBOFLAVIN)"). Our logic explicitly handles sectioning detecting where ingredient lists start discarding specific footers effectively isolating core data. The logic iterates identifying common comma structures parsing sub-components explicitly stripping out quantitative variables safely referencing underlying string dictionaries ensuring `wheat flour` normalizes strictly discarding chemical compounds gracefully standardizing outputs reliably referencing database identifiers globally effectively checking constraint lists natively. 
