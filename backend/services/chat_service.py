"""
NutriVision - Chat Service

Gemini integration with safe fallback responses.
"""

import asyncio
import os
from typing import Any, Optional

import requests


GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def _safe_fallback(question: str, has_context: bool) -> str:
    base = (
        "I could not reach the AI service right now. "
        "Please try again in a moment. "
        "I can still give general nutrition guidance if you ask a simple question."
    )
    if has_context:
        base += " I will use your scan details once the connection is available."

    q = question.lower()
    if any(
        k in q
        for k in ["diabetes", "kid", "kids", "child", "children", "heart", "weight", "allergy"]
    ):
        base += " For condition-specific advice, consult a qualified healthcare professional."

    return base


def _build_prompt(
    question: str,
    scan_context: Optional[dict[str, Any]],
    user_profile: Optional[dict[str, Any]],
) -> str:
    context_text = "Not available"
    user_profile_text = "Not available"
    if scan_context:
        context_text = str(scan_context)
    if user_profile:
        user_profile_text = str(user_profile)

    return (
        "You are NutriVision AI, a mobile food-label, nutrition, ingredient, and health-awareness assistant.\n\n"
        "MISSION:\n"
        "Help users understand food products and make better choices using real scan data first, user profile second, and general nutrition knowledge third.\n\n"
        "MODES:\n"
        "1. Scan AI mode:\n"
        "- Use scan_context as the main source of truth.\n"
        "- Use user_profile if available.\n"
        "- Explain the scanned product clearly and simply.\n"
        "- Cover product identity, ingredient insights, nutrition, allergens, dietary suitability, and practical advice.\n"
        "- If product match confidence or OCR confidence is low, clearly say the result may be uncertain.\n"
        "- If needed, ask one short clarification question before giving a strong conclusion.\n\n"
        "2. General AI mode:\n"
        "- If scan_context is missing, answer general food, nutrition, ingredient, calorie, diet, and health-awareness questions normally.\n"
        "- Use user_profile if available for personalization.\n"
        "- Do not invent product-specific facts.\n\n"
        "STRICT RULES:\n"
        "- Never invent product names, ingredients, allergens, or nutrition values.\n"
        "- Never claim certainty when OCR or product match confidence is low.\n"
        "- Never say a product is safe for an allergy unless the data clearly supports it.\n"
        "- Never provide medical diagnosis, prescriptions, treatment plans, or emergency instructions.\n"
        "- Keep tone calm, practical, and trustworthy for a health-tech app.\n"
        "- Use simple mobile-friendly language.\n"
        "- Prefer short paragraphs and bullets.\n"
        "- Keep answers practical, trustworthy, and easy to understand.\n\n"
        "WHEN scan_context EXISTS:\n"
        "Answer in this order:\n"
        "1. Product identified\n"
        "2. Confidence note if needed\n"
        "3. Nutrition overview\n"
        "4. Ingredient insights\n"
        "5. Allergen check\n"
        "6. Dietary suitability\n"
        "7. Practical recommendation\n\n"
        "IF confidence is low:\n"
        "- say what is uncertain,\n"
        "- mention whether product match, OCR text, or ingredient extraction is weak,\n"
        "- suggest retaking the scan or confirming the product name.\n\n"
        "OUTPUT STYLE:\n"
        "- Keep responses concise for mobile, but include actionable value.\n"
        "- Use short bullets where helpful.\n"
        "- If user_profile exists, tailor guidance to allergies and dietary preferences.\n\n"
        "WHEN scan_context DOES NOT EXIST:\n"
        "Answer like a helpful general AI for nutrition and health-awareness topics.\n\n"
        f"SCAN_CONTEXT:\n{context_text}\n\n"
        f"USER_PROFILE:\n{user_profile_text}\n\n"
        f"QUESTION:\n{question}"
    )


def _gemini_request(url: str, payload: dict[str, Any]) -> requests.Response:
    return requests.post(url, json=payload, timeout=20)


async def generate_chat_answer(
    question: str,
    scan_context: Optional[dict[str, Any]],
    user_profile: Optional[dict[str, Any]] = None,
) -> tuple[str, str]:
    api_key = os.getenv("GEMINI_API_KEY")
    has_context = bool(scan_context)

    if not api_key:
        return (
            "NutriVision AI is not configured yet. Please add the Gemini API key and try again.",
            "fallback",
        )

    prompt = _build_prompt(question, scan_context, user_profile)
    url = f"{GEMINI_API_BASE}/{GEMINI_MODEL}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 350
        }
    }

    try:
        response = await asyncio.to_thread(_gemini_request, url, payload)
        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates") or []
        if not candidates:
            return _safe_fallback(question, has_context), "fallback"

        content = candidates[0].get("content", {})
        parts = content.get("parts") or []
        if not parts:
            return _safe_fallback(question, has_context), "fallback"

        text_parts = [
            part.get("text", "").strip()
            for part in parts
            if isinstance(part, dict) and part.get("text")
        ]
        text = "\n".join(p for p in text_parts if p).strip()

        if not text:
            return _safe_fallback(question, has_context), "fallback"

        return text, "gemini"

    except requests.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else None
        print("Gemini chat error:", repr(e))

        if status_code == 429:
            return (
                "NutriVision AI is temporarily busy because the Gemini request limit was reached. "
                "Please wait a little and try again.",
                "fallback",
            )

        if status_code == 503:
            return (
                "NutriVision AI is temporarily unavailable right now. "
                "Please try again after some time.",
                "fallback",
            )

        if status_code in (401, 403):
            return (
                "NutriVision AI could not authenticate with the Gemini service. "
                "Please check the API key configuration.",
                "fallback",
            )

        if status_code == 404:
            return (
                "NutriVision AI could not find the configured Gemini model. "
                "Please verify the model name in the backend.",
                "fallback",
            )

        return _safe_fallback(question, has_context), "fallback"
    except Exception:
        return _safe_fallback(question, has_context), "fallback"