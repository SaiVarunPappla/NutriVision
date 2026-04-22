"""
NutriVision - Scan API Routes

Handles image and text-based food scanning requests.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.scan import TextScanRequest, ScanResponse
from models.ingredient import IngredientResponse
from models.nutrition import NutritionSummary, DietarySuitability
from integrations.base_nutrition_api import NutrientData
from models.recommendation import RecommendationItem
import uuid
import logging
from typing import Optional, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

from services.ingredient_parser import parse_ingredients_with_metadata
from services.nutrition_service import lookup_branded_nutrition, lookup_nutrition
from services.allergen_service import detect_allergens
from services.diet_service import check_dietary_suitability
from services.recommendation_service import generate_recommendations, calculate_health_score
from services.ocr_service import extract_text_from_image
from services.ocr_normalizer_service import normalize_ocr_label
from services.firestore_service import create_scan, save_history_entry

MIN_PRODUCT_NAME_CONFIDENCE = 0.70


@router.post(
    "/scan/text",
    response_model=ScanResponse,
    summary="Analyze Text Ingredients",
    description="Analyze a list of ingredients provided as text input."
)
async def scan_text(request: TextScanRequest):
    """
    Accepts raw ingredient text, parses it, and returns full nutritional analysis.
    """
    scan_id = f"scan_{uuid.uuid4().hex[:8]}"

    nutrition_summary = NutritionSummary()
    per_ingredient_data_raw: List[Any] = []
    detected_allergens = []
    dietary_suitability = DietarySuitability()
    recommendations = []
    health_score = 0.0
    final_scan_type = "text"
    final_status_message = "Analysis completed."
    ingredients: List[IngredientResponse] = []

    if request.product_name and request.product_name.strip():
        logger.info(f"[Scan/Text] Attempting branded lookup for: {request.product_name}")
        branded_summary, branded_ingredients_data, branded_status_msg = await lookup_branded_nutrition(
            request.product_name
        )

        if branded_summary and branded_summary.overall_matched_type != "no_match":
            nutrition_summary = branded_summary
            per_ingredient_data_raw = branded_ingredients_data

            primary_nutrient_info = branded_ingredients_data[0] if branded_ingredients_data else None
            if isinstance(primary_nutrient_info, NutrientData):
                ingredients = [
                    IngredientResponse(
                        ingredient_id=f"ing_{uuid.uuid4().hex[:6]}",
                        name=request.product_name,
                        normalized_name=request.product_name.lower(),
                        position=1,
                        match_confidence=primary_nutrient_info.confidence,
                        nutrition_source=primary_nutrient_info.source,
                        matched_name=primary_nutrient_info.matched_name,
                        matched_type=primary_nutrient_info.matched_type,
                        usda_fdc_id=primary_nutrient_info.fdc_id,
                    )
                ]
            else:
                ingredients = [
                    IngredientResponse(
                        ingredient_id=f"ing_{uuid.uuid4().hex[:6]}",
                        name=request.product_name,
                        normalized_name=request.product_name.lower(),
                        position=1,
                        match_confidence=0.5,
                        nutrition_source="Unknown",
                        matched_name=request.product_name,
                        matched_type="estimated_product",
                        usda_fdc_id=None,
                    )
                ]

            allergen_result = detect_allergens(ingredients)
            detected_allergens = allergen_result["detected"]
            dietary_suitability = check_dietary_suitability(ingredients)
            recommendations = generate_recommendations(
                nutrition=nutrition_summary,
                allergens=detected_allergens,
                dietary_suitability=dietary_suitability,
            )
            health_score = calculate_health_score(nutrition_summary, detected_allergens)
            final_scan_type = "branded_text"
            final_status_message = branded_status_msg

            logger.info(f"[Scan/Text] Branded lookup successful and processed for: {request.product_name}")

    if not nutrition_summary.overall_matched_type or nutrition_summary.overall_matched_type == "no_match":
        logger.info(
            f"[Scan/Text] Branded lookup failed or not applicable for: '{request.product_name}'. "
            f"Falling back to ingredient parsing."
        )
        nlp_result = await parse_ingredients_with_metadata(request.text)
        ingredients = nlp_result["ingredients"]

        if not ingredients:
            final_status_message = "No recognizable ingredients found in the provided text."
            logger.warning("[Scan/Text] No ingredients parsed from text.")
        else:
            nutrition_summary, per_ingredient_data_raw, nutrition_status_msg = await lookup_nutrition(ingredients)
            allergen_result = detect_allergens(ingredients)
            detected_allergens = allergen_result["detected"]
            dietary_suitability = check_dietary_suitability(ingredients)
            recommendations = generate_recommendations(
                nutrition=nutrition_summary,
                allergens=detected_allergens,
                dietary_suitability=dietary_suitability,
            )
            health_score = calculate_health_score(nutrition_summary, detected_allergens)
            final_scan_type = "text_ingredients"
            final_status_message = (
                nutrition_status_msg if nutrition_status_msg else "Ingredient analysis completed."
            )
            logger.info(f"[Scan/Text] Ingredient-level analysis completed. Status: {final_status_message}")

    ingredient_responses = []
    for ing in ingredients:
        matched_item_data = None

        if isinstance(ing, IngredientResponse) and ing.normalized_name:
            for item in per_ingredient_data_raw:
                nutrient_data_obj = None

                if isinstance(item, NutrientData):
                    nutrient_data_obj = item
                elif isinstance(item, dict):
                    potential_nutrient_data = item.get("nutrition")
                    if isinstance(potential_nutrient_data, NutrientData):
                        nutrient_data_obj = potential_nutrient_data

                if nutrient_data_obj and nutrient_data_obj.normalized_name == ing.normalized_name:
                    matched_item_data = nutrient_data_obj
                    break
                elif isinstance(item, dict) and item.get("name") == ing.normalized_name:
                    matched_item_data = item
                    break

        usda_fdc_id = None
        matched_name = None
        matched_type = None
        match_confidence = ing.match_confidence if isinstance(ing, IngredientResponse) else 0.0
        nutrition_source = None

        if matched_item_data:
            if isinstance(matched_item_data, NutrientData):
                usda_fdc_id = matched_item_data.fdc_id
                matched_name = matched_item_data.matched_name
                matched_type = matched_item_data.matched_type
                nutrition_source = matched_item_data.source
                if final_scan_type == "branded_text":
                    match_confidence = max(match_confidence, matched_item_data.confidence)
            elif isinstance(matched_item_data, dict):
                usda_fdc_id = matched_item_data.get("fdc_id")
                matched_name = matched_item_data.get("matched_name")
                matched_type = matched_item_data.get("matched_type")
                nutrition_source = matched_item_data.get("source")
                confidence_from_dict = matched_item_data.get("confidence")
                if confidence_from_dict is not None and isinstance(confidence_from_dict, (int, float)):
                    match_confidence = max(match_confidence, float(confidence_from_dict))

        ingredient_responses.append(
            IngredientResponse(
                ingredient_id=f"ing_{uuid.uuid4().hex[:6]}",
                name=ing.name,
                normalized_name=ing.normalized_name,
                position=ing.position,
                usda_fdc_id=usda_fdc_id,
                match_confidence=match_confidence,
                nutrition_source=nutrition_source,
                matched_name=matched_name,
                matched_type=matched_type,
            )
        )

    response = ScanResponse(
        scan_id=scan_id,
        status="completed",
        scan_type=final_scan_type,
        product_name=(
            request.product_name
            if request.product_name and request.product_name.strip()
            else (nutrition_summary.overall_matched_name if nutrition_summary.overall_matched_name else None)
        ),
        extracted_text=request.text,
        ingredients=ingredient_responses,
        nutrition=nutrition_summary,
        allergens=detected_allergens,
        dietary_suitability=dietary_suitability,
        health_score=health_score,
        recommendations=recommendations,
        status_message=final_status_message,
    )

    await create_scan({
        "scan_id": scan_id,
        "user_id": request.user_id,
        "scan_type": final_scan_type,
        "input_text": request.text,
        "status": "completed",
        "status_message": final_status_message,
    })

    history_data = response.model_dump()
    history_data["history_id"] = scan_id
    history_data["user_id"] = request.user_id
    await save_history_entry(history_data)

    return response


@router.post(
    "/scan/image",
    response_model=ScanResponse,
    summary="Analyze Food Image",
    description="Upload a food label image for OCR-based ingredient analysis."
)
async def scan_image(
        image: UploadFile = File(..., description="Food label image (JPEG/PNG)"),
        user_id: str = Form(..., description="Firebase Auth UID"),
        product_name: Optional[str] = Form(None, description="Optional product name"),
):
    """
    Accepts a food label image, extracts text via OCR, and returns analysis.
    """
    content_type = image.content_type
    logger.info(f"Received image with content type: {content_type}")
    if content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        logger.warning(f"Unsupported image format received: {content_type}")
        raise HTTPException(
            status_code=400,
            detail="Invalid image format. Please upload a JPG, JPEG, or PNG image."
        )

    scan_id = f"scan_{uuid.uuid4().hex[:8]}"

    nutrition_summary = NutritionSummary()
    per_ingredient_data_raw: List[Any] = []
    detected_allergens = []
    dietary_suitability = DietarySuitability()
    recommendations = []
    health_score = 0.0
    final_scan_type = "image"
    final_status_message = "Analysis completed."
    ingredients: List[IngredientResponse] = []
    extracted_text = ""
    normalized_label = None
    ocr_confidence = 0.0
    ocr_source = "unknown"
    branded_status_msg = None

    try:
        image_bytes = await image.read()
        ocr_result = await extract_text_from_image(image_bytes)
        extracted_text = ocr_result.get("text", "")
        ocr_confidence_raw = ocr_result.get("confidence", 0.0)

        if isinstance(ocr_confidence_raw, (int, float)):
            ocr_confidence = float(ocr_confidence_raw)
            if ocr_confidence > 1:
                ocr_confidence = ocr_confidence / 100.0
        else:
            ocr_confidence = 0.0

        ocr_confidence = round(ocr_confidence, 2)
        ocr_source = ocr_result.get("source", "unknown")

        logger.info(
            f"OCR extracted text (confidence: {ocr_confidence * 100:.1f}%, source: {ocr_source}): "
            f"{extracted_text[:100]}..."
        )
    except Exception as e:
        logger.error(f"Error during OCR processing: {e}", exc_info=True)
        return ScanResponse(
            scan_id=scan_id,
            status="failed",
            scan_type="image_ocr_failed",
            product_name=product_name,
            extracted_text="",
            ingredients=[],
            nutrition=NutritionSummary(),
            allergens=[],
            dietary_suitability=DietarySuitability(),
            health_score=0.0,
            recommendations=[
                RecommendationItem(
                    type="warning",
                    title="OCR Processing Failed",
                    message="Could not process the image for text extraction. Please try again.",
                    severity="high"
                )
            ],
            status_message="Failed to extract text from the image.",
        )

    if ocr_source == "demo":
        logger.warning("[Scan/Image] Demo OCR detected. Rejecting fake OCR result.")
        return ScanResponse(
            scan_id=scan_id,
            status="failed",
            scan_type="image_demo_ocr_rejected",
            product_name=product_name,
            extracted_text="",
            ingredients=[],
            nutrition=NutritionSummary(),
            allergens=[],
            dietary_suitability=DietarySuitability(),
            health_score=0.0,
            recommendations=[
                RecommendationItem(
                    type="warning",
                    title="Real OCR Unavailable",
                    message="Server-side OCR is unavailable. Please use on-device scan or try again later.",
                    severity="high"
                )
            ],
            status_message="Demo OCR fallback rejected. Real OCR only mode is enabled.",
        )

    if not extracted_text:
        logger.warning("OCR returned no text.")
        return ScanResponse(
            scan_id=scan_id,
            status="failed",
            scan_type="image_no_text",
            product_name=product_name,
            extracted_text="",
            ingredients=[],
            nutrition=NutritionSummary(),
            allergens=[],
            dietary_suitability=DietarySuitability(),
            health_score=0.0,
            recommendations=[
                RecommendationItem(
                    type="warning",
                    title="Extraction Failed",
                    message="Could not extract any text from the provided image. Please try again with a clearer image.",
                    severity="high"
                )
            ],
            status_message="OCR failed to extract any text from the image.",
        )

    try:
        normalized_label = await normalize_ocr_label(extracted_text)
    except Exception:
        normalized_label = None

    search_product_name = None
    branded_candidates: List[str] = []
    allow_branded_lookup = True
    normalized_name_confidence = None

    if product_name and product_name.strip():
        search_product_name = product_name.strip()
        branded_candidates.append(search_product_name)
    else:
        if isinstance(normalized_label, dict):
            normalized_display_name = (normalized_label.get("clean_display_name") or "").strip()
            normalized_product_name = (normalized_label.get("product_name") or "").strip()
            alternatives = normalized_label.get("possible_alternatives") or []
            normalized_name_confidence_raw = normalized_label.get("name_confidence")
            if isinstance(normalized_name_confidence_raw, (int, float)):
                normalized_name_confidence = float(normalized_name_confidence_raw)

            if normalized_display_name:
                branded_candidates.append(normalized_display_name)
            if normalized_product_name and normalized_product_name not in branded_candidates:
                branded_candidates.append(normalized_product_name)

            if isinstance(alternatives, list):
                for alt in alternatives:
                    alt_text = str(alt).strip()
                    if alt_text and alt_text not in branded_candidates:
                        branded_candidates.append(alt_text)

            if normalized_name_confidence is not None and normalized_name_confidence < MIN_PRODUCT_NAME_CONFIDENCE:
                allow_branded_lookup = False

        first_line = extracted_text.split("\n")[0].strip() if extracted_text else ""
        looks_like_ingredient_list = (
                first_line.upper().startswith("INGREDIENTS")
                or "," in first_line
                or "(" in first_line
                or len(first_line) > 60
        )
        if not branded_candidates and first_line and not looks_like_ingredient_list:
            branded_candidates.append(first_line)

    if branded_candidates:
        search_product_name = branded_candidates[0]

    if not allow_branded_lookup and normalized_name_confidence is not None:
        logger.info(
            f"[Scan/Image] Normalized product name confidence {normalized_name_confidence:.2f} < "
            f"{MIN_PRODUCT_NAME_CONFIDENCE:.2f}; skipping branded lookup and using ingredient fallback."
        )
        final_status_message = "Product name confidence is low; using ingredient-level analysis."

    if allow_branded_lookup and branded_candidates:
        for candidate_name in branded_candidates:
            logger.info(f"[Scan/Image] Attempting branded lookup for: {candidate_name}")
            candidate_summary, candidate_ingredients_data, candidate_status_msg = await lookup_branded_nutrition(
                candidate_name
            )

            if not candidate_summary or candidate_summary.overall_matched_type == "no_match":
                branded_status_msg = candidate_status_msg
                continue

            candidate_confidence = 0.0
            primary_nutrient_info = candidate_ingredients_data[0] if candidate_ingredients_data else None
            if isinstance(primary_nutrient_info, NutrientData):
                candidate_confidence = float(primary_nutrient_info.confidence or 0.0)
            elif isinstance(candidate_summary.overall_confidence, (int, float)):
                candidate_confidence = float(candidate_summary.overall_confidence)

            if candidate_confidence < MIN_PRODUCT_NAME_CONFIDENCE:
                branded_status_msg = (
                    f"Branded match for '{candidate_name}' was too weak "
                    f"({candidate_confidence:.2f}); trying next candidate or falling back."
                )
                logger.info(f"[Scan/Image] {branded_status_msg}")
                continue

            search_product_name = candidate_name
            branded_summary = candidate_summary
            branded_ingredients_data = candidate_ingredients_data
            branded_status_msg = candidate_status_msg

            nutrition_summary = branded_summary
            per_ingredient_data_raw = branded_ingredients_data

            if isinstance(primary_nutrient_info, NutrientData):
                ingredients = [
                    IngredientResponse(
                        ingredient_id=f"ing_{uuid.uuid4().hex[:6]}",
                        name=search_product_name,
                        normalized_name=search_product_name.lower(),
                        position=1,
                        match_confidence=primary_nutrient_info.confidence,
                        nutrition_source=primary_nutrient_info.source,
                        matched_name=primary_nutrient_info.matched_name,
                        matched_type=primary_nutrient_info.matched_type,
                        usda_fdc_id=primary_nutrient_info.fdc_id,
                    )
                ]
            else:
                ingredients = [
                    IngredientResponse(
                        ingredient_id=f"ing_{uuid.uuid4().hex[:6]}",
                        name=search_product_name,
                        normalized_name=search_product_name.lower(),
                        position=1,
                        match_confidence=max(candidate_confidence, 0.5),
                        nutrition_source="Unknown",
                        matched_name=search_product_name,
                        matched_type="estimated_product",
                        usda_fdc_id=None,
                    )
                ]

            allergen_result = detect_allergens(ingredients)
            detected_allergens = allergen_result["detected"]
            dietary_suitability = check_dietary_suitability(ingredients)
            recommendations = generate_recommendations(
                nutrition=nutrition_summary,
                allergens=detected_allergens,
                dietary_suitability=dietary_suitability,
            )
            health_score = calculate_health_score(nutrition_summary, detected_allergens)
            final_scan_type = "branded_image"
            final_status_message = branded_status_msg
            logger.info(f"[Scan/Image] Branded lookup successful and processed for: {search_product_name}")
            break

    if not nutrition_summary.overall_matched_type or nutrition_summary.overall_matched_type == "no_match":
        if search_product_name and branded_status_msg:
            logger.info(
                f"[Scan/Image] Branded lookup failed/not found for: '{search_product_name}'. "
                f"Falling back to ingredient parsing."
            )
            final_status_message = branded_status_msg
        else:
            logger.info(
                "[Scan/Image] No product name for branded lookup or it appears to be an ingredient list. "
                "Proceeding with ingredient parsing."
            )
            final_status_message = "Proceeding with ingredient analysis."

        try:
            nlp_result = await parse_ingredients_with_metadata(extracted_text)
            ingredients = nlp_result.get("ingredients", [])

            if not ingredients:
                logger.warning("No ingredients parsed from OCR text.")
                final_status_message = "No recognizable ingredients found after OCR."
            else:
                nutrition_summary, per_ingredient_data_raw, nutrition_status_msg = await lookup_nutrition(ingredients)
                allergen_result = detect_allergens(ingredients)
                detected_allergens = allergen_result["detected"]
                dietary_suitability = check_dietary_suitability(ingredients)
                recommendations = generate_recommendations(
                    nutrition=nutrition_summary,
                    allergens=detected_allergens,
                    dietary_suitability=dietary_suitability,
                )
                health_score = calculate_health_score(nutrition_summary, detected_allergens)
                final_scan_type = "image_ingredients"
                final_status_message = (
                    nutrition_status_msg if nutrition_status_msg else "Ingredient analysis completed."
                )
                logger.info(f"[Scan/Image] Ingredient-level analysis completed. Status: {final_status_message}")

        except Exception as e:
            logger.error(f"Error during ingredient parsing or analysis: {e}", exc_info=True)
            return ScanResponse(
                scan_id=scan_id,
                status="failed",
                scan_type="image_analysis_failed",
                product_name=search_product_name if search_product_name else product_name,
                extracted_text=extracted_text,
                ingredients=[],
                nutrition=NutritionSummary(),
                allergens=[],
                dietary_suitability=DietarySuitability(),
                health_score=0.0,
                recommendations=[
                    RecommendationItem(
                        type="warning",
                        title="Analysis Failed",
                        message="An error occurred during ingredient analysis. Please try again.",
                        severity="high"
                    )
                ],
                status_message="Failed to analyze ingredients.",
            )

    if ocr_source == "tesseract" and ocr_confidence < 0.60:
        recommendations.append(
            RecommendationItem(
                type="info",
                title="Low OCR Confidence",
                message=(
                    f"Text was extracted with {ocr_confidence * 100:.0f}% average confidence. "
                    f"Double-check the extracted text and analysis results."
                ),
                severity="low"
            )
        )

    ingredient_responses = []
    for ing in ingredients:
        matched_item_data = None

        for item in per_ingredient_data_raw:
            nutrient_data_obj = None

            if isinstance(item, NutrientData):
                nutrient_data_obj = item
            elif isinstance(item, dict):
                potential_nutrient_data = item.get("nutrition")
                if isinstance(potential_nutrient_data, NutrientData):
                    nutrient_data_obj = potential_nutrient_data

            if nutrient_data_obj and nutrient_data_obj.normalized_name == ing.normalized_name:
                matched_item_data = nutrient_data_obj
                break
            elif isinstance(item, dict) and item.get("name") == ing.normalized_name:
                matched_item_data = item
                break

        usda_fdc_id = None
        matched_name = None
        matched_type = None
        match_confidence = ing.match_confidence if isinstance(ing, IngredientResponse) else ocr_confidence
        nutrition_source = None

        if matched_item_data:
            if isinstance(matched_item_data, NutrientData):
                usda_fdc_id = matched_item_data.fdc_id
                matched_name = matched_item_data.matched_name
                matched_type = matched_item_data.matched_type
                nutrition_source = matched_item_data.source
                if final_scan_type.startswith("branded"):
                    match_confidence = max(match_confidence, matched_item_data.confidence)
            elif isinstance(matched_item_data, dict):
                usda_fdc_id = matched_item_data.get("fdc_id")
                matched_name = matched_item_data.get("matched_name")
                matched_type = matched_item_data.get("matched_type")
                nutrition_source = matched_item_data.get("source")
                confidence_from_dict = matched_item_data.get("confidence")
                if confidence_from_dict is not None and isinstance(confidence_from_dict, (int, float)):
                    match_confidence = max(match_confidence, float(confidence_from_dict))

        ingredient_responses.append(
            IngredientResponse(
                ingredient_id=f"ing_{uuid.uuid4().hex[:6]}",
                name=ing.name,
                normalized_name=ing.normalized_name,
                position=ing.position,
                usda_fdc_id=usda_fdc_id,
                match_confidence=match_confidence,
                nutrition_source=nutrition_source,
                matched_name=matched_name,
                matched_type=matched_type,
            )
        )

    response = ScanResponse(
        scan_id=scan_id,
        status="completed",
        scan_type=final_scan_type,
        product_name=(
            product_name
            if product_name and product_name.strip()
            else (nutrition_summary.overall_matched_name if nutrition_summary.overall_matched_name else None)
        ),
        extracted_text=extracted_text,
        ingredients=ingredient_responses,
        nutrition=nutrition_summary,
        allergens=detected_allergens,
        dietary_suitability=dietary_suitability,
        health_score=health_score,
        recommendations=recommendations,
        status_message=final_status_message,
    )

    await create_scan({
        "scan_id": scan_id,
        "user_id": user_id,
        "scan_type": final_scan_type,
        "input_text": extracted_text,
        "status": "completed",
        "status_message": final_status_message,
    })

    history_data = response.model_dump()
    history_data["history_id"] = scan_id
    history_data["user_id"] = user_id
    await save_history_entry(history_data)

    return response


@router.get(
    "/scan/{scan_id}",
    response_model=ScanResponse,
    summary="Get Scan Details",
    description="Retrieve details of a previously completed scan."
)
async def get_scan(scan_id: str):
    """Retrieve a specific scan result by its ID from Firestore."""
    logger.warning(f"Get scan details for {scan_id} - Firestore integration pending.")
    raise HTTPException(
        status_code=404,
        detail=f"Scan '{scan_id}' not found. Firestore integration pending."
    )