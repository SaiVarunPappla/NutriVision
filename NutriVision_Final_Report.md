# NutriVision – AI-Based Ingredient Analysis System
**Final Project Report**

## 1. Abstract
NutriVision is an innovative Android application combining Computer Vision (CV) and Natural Language Processing (NLP) to decipher complex food ingredient labels. With rising dietary restrictions, allergies, and health-consciousness, consumers struggle to understand obscure additive names or evaluate nutritional trade-offs rapidly. NutriVision solves this by allowing users to scan food labels or manually type ingredients. The system utilizes Optical Character Recognition (OCR) to extract text, NLP to normalize and analyze ingredients, and the USDA FoodData Central API to provide comprehensive nutritional profiles. It features a robust rule-based engine determining dietary suitability (e.g., vegan, keto) and actively flags dangerous allergens (Big 14).

## 2. Introduction
Understanding food content requires navigating dense text and complex chemical names. NutriVision bridges the gap between intricate industrial food ingredient formulations and the everyday consumer. By leveraging an Android frontend interface linked asynchronously to a high-performance Python FastAPI backend, the system aggregates external nutrition APIs to generate a holistic, easily readable "Health Score" paired with actionable dietary warnings. 

## 3. Problem Statement
Many consumers find it difficult to identify hidden allergens or determine if a product fits their dietary requirements (e.g., gluten-free, vegan) due to complex, microscopic tracking labels utilizing scientific synonyms. Current market alternatives often rely exclusively on barcode scanning, failing entirely on obscure, imported, or newly packaged items not yet registered in proprietary databases.

## 4. Objectives
- Design a scalable mobile-first interface allowing ingredient extraction directly from text or images.
- Develop an AI pipeline capable of preprocessing, extracting, and standardizing label text. 
- Build an interconnected microservice architecture grading health scores, identifying 14 major allergens, and confirming 6 specific dietary constraints dynamically.
- Provide secure personal profile configurations allowing users to filter tracking against their explicit genetic or chosen dietary constraints.

## 5. Scope
The application targets Android platforms natively encompassing image-capturing architectures alongside manual input fallbacks. The backend handles REST API allocations prioritizing USDA FoodData Central databases natively, backed entirely by a robust "Offline Demo Fallback" mechanism guaranteeing usability during external API outages. Data persistence is managed implicitly using NoSQL Firebase/Firestore.

## 6. Functional Requirements
1. **User Authentication:** Registration, login, and secure sessions tracking user UUIDs.
2. **Ingredient Scanning:** Image uploads mapped to OCR pipelines alongside direct text ingestion.
3. **Dietary Profiling:** Explicit tracking of personal allergies and lifestyle diets evaluating interactions proactively.
4. **Result Generation:** Outputting calculated Health Scores alongside specific warnings and positive highlights dynamically.
5. **History Tracking:** Storing localized analysis responses permitting users to revisit past scans safely.

## 7. Non-Functional Requirements
1. **Performance:** Backend NLP and OCR must resolve text extraction algorithms swiftly preventing UI timeouts.
2. **Offline Resilience:** Must simulate network paths falling back to local dictionaries actively bypassing server unavailability (Viva-friendly).
3. **Usability:** Single-Action application flows enforcing minimalistic intuitive interactions.
4. **Security:** Rest API traffic targeting Emulators locally overriding HTTPS requirements efficiently targeting internal proxies (`10.0.2.2`).

## 8. Literature Survey Outline
1. **Optical Character Recognition in Retail:** Evaluation of PyTesseract capabilities adapting strictly to distorted, non-linear text formats typical on plastic packaging.
2. **NLP Text Normalization:** Structuring algorithms stripping percentages out, removing parenthetic blocks, grouping synonyms (e.g., "high fructose corn syrup" $\rightarrow$ "sugar").
3. **Nutritional Data Abstraction:** Utilizing USDA APIs vs Edamam APIs comparing throughputs and hierarchical structures supporting rule-based dietary evaluations.

## 9. Existing System
Historically, applications primarily utilized Barcode (UPC) integrations directly querying relational databases. They suffer massive blind spots analyzing bakery goods, restaurant menus, and unrecognized foreign imports. They heavily depend on static vendor-supplied metadata which frequently lacks transparent ingredient-level granularity. 

## 10. Proposed System
NutriVision bypasses UPC barcode reliance by directly reading the physical ingredient list itself using OCR. This enforces a universal analysis framework operating successfully even if the product itself is actively unlisted, translating raw chemical strings into an aggregated, personalized diagnostic dynamically.

## 11. Methodology
Agile deployment utilized scaling the architecture modularly:
1. **Foundation Model:** Defined Firestore Schemas identifying data encapsulation rules.
2. **Algorithm Phase:** Engineered image sharpening utilizing OpenCV standardizing inputs for PyTesseract.
3. **API & Service Logic:** Mapped logic routing USDA dictionaries against NLP normalized outputs evaluating Health constraints utilizing a point-deduction algorithm.
4. **Android Client UI:** Wrapped Retrofit Kotlin coroutines binding Material Design interactive cards tracking user states effectively.

## 12. Module Descriptions
1. **Image Preprocessor Module:** OpenCV pipelines resolving grayscale filtering, binary thresholding, denoising, and deskewing maximizing geometric readability.
2. **NLP Processor Module:** Identifying section headers (e.g. "Ingredients:"), filtering grammar, mapping synonyms, deduping outputs.
3. **Nutrition Service:** Reaching out externally mapping ingredients dynamically compiling aggregated macros (Calories, Proteins) against known USDA IDs.
4. **Recommendation Engine:** Rule-based algorithm generating discrete categorized flags (`warning`, `info`, `allergen_alert`).

## 13. Algorithms Used
- **Adaptive Thresholding (OpenCV):** Transforms contrasting images separating foreground text elements from packaging backgrounds regardless of ambient lighting dynamically.
- **Levenshtein Distance / NLP Matching:** Standardizes misspelled or complex text fragments targeting established baseline ingredient dictionaries preventing duplicate parsing. 
- **Rule-Based Dietary Heuristics:** Boolean flags mapping dictionary arrays explicitly tracking cross-contaminations efficiently (ex. if `ingredient` in `dairy_list` $\rightarrow$ `is_vegan` = False).

## 14. System Architecture
NutriVision utilizes a **Client-Server Architecture**. 
Android operates strictly as a Presentation layer executing logic solely communicating externally via Retrofit REST clients tracking Data encapsulation. The **FastAPI** server operates exclusively as a Stateless mediator dispatching complex algorithmic logic downwards asynchronously returning Pydantic structures natively mapped returning standardized JSON payloads. External Dependencies (Firebase/USDA) attach independently to server contexts.

## 15. Firestore Schema Explanation
- **Users Table**: Maps simple authentication paths (`uid`, `email`, `allergies`, `dietary_preferences`).
- **Scans Table**: Tracks individual evaluations maintaining the origin string, parsed JSON Arrays, referenced ID vectors, and aggregated `health_score`.
- **Ingredients Table**: Persistent caching mechanism cataloging previously aggregated macros reducing external USDA bottlenecks rapidly mapping `normalized_name` attributes.

## 16. API Explanation
- `/v1/scan/text` & `/v1/scan/image`: Core engines. Triggers the internal OCR or ingestion strings, executes dietary services, caches to Firebase, and returns a grouped `ScanResponse`.
- `/v1/history/{user_id}`: Rapidly pulls metadata references bypassing full evaluation pipelines displaying chronological references. 
- `/v1/health`: Server ping endpoint mapping internal dependencies explicitly checking external API integrity mappings.

## 17. Testing Strategy
- **Unit Testing:** 105 explicit Python `pytest` targets mocking external API paths strictly verifying internal Algorithm precision enforcing high confidence.
- **Integration Testing:** Booting local Uvicorn paths actively validating Retrofit Android deserialization bindings locally across Coroutines properly extracting Pydantic architectures gracefully.
- **Failsafe / Offline Testing:** Validated specific fallback mechanisms simulating database outages guaranteeing "Demo Mode" integrity. 

## 18. Results and Discussion
The framework successfully bridges dynamic ingredient strings translating arbitrary packaging safely into human-readable alerts rapidly matching backend standards avoiding timeout risks through robust asynchronous handling paths mapping 14 significant allergens efficiently.

## 19. Conclusion
NutriVision provides a reliable, scalable proof-of-concept demonstrating how localized AI systems and heuristic algorithms completely restructure physical food label evaluations seamlessly prioritizing User Accessibility reliably bypassing reliance purely on standard UPC barcode infrastructures.

## 20. Future Scope
- Expand ML capabilities incorporating localized TFLite object-detection scanning specific packaging environments immediately identifying macro-regions explicitly prior to OCR ingestion.
- Expand multi-lingual dataset tracking automatically converting foreign ingredients mapping outwards onto standard English definitions utilizing translation layers. 
- Implement Cloud Vision APIs as a production-grade external fallback if Tesseract confidence flags fall inherently low natively.
