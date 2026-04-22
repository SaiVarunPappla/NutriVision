"""
NutriVision - OCR Normalizer Service

Normalizes noisy OCR into structured label data before branded lookup.
"""

import asyncio
import json
import os
from typing import Any

import requests


GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def _default_result(ocr_text: str) -> dict[str, Any]:
    first_line = ""
    for line in (ocr_text or "").splitlines():
        candidate = line.strip()
        if candidate:
            first_line = candidate
            break

    return {
        "brand_name": "",
        "product_name": first_line.title() if first_line else "",
        "flavor_or_variant": "",
        "clean_display_name": first_line.title() if first_line else "",
        "raw_visible_name": first_line,
        "ignored_marketing_text": [],
        "possible_alternatives": [],
        "name_confidence": 0.4 if first_line else 0.0,
        "needs_manual_review": True,
        "reason": "Fallback parser used because Gemini normalization was unavailable."
    }


def _prompt(ocr_text: str) -> str:
    return (
        "You are NutriVision Product Resolver.\n\n"
        "TASK:\n"
        "Convert noisy food-package OCR into the most accurate possible visible product identity without guessing.\n\n"
        "NON-NEGOTIABLE RULES:\n"
        "1. Use ONLY the OCR text provided.\n"
        "2. Do NOT invent unseen brands, products, flavors, ingredients, or nutrition facts.\n"
        "3. Prefer the most visible sellable product name from the front label.\n"
        "4. Ignore slogans and marketing claims.\n"
        "5. Correct OCR mistakes only when the correction is obvious.\n"
        "6. If confidence is low, preserve the visible text and mark low confidence.\n"
        "7. If there are multiple plausible names, rank them.\n"
        "8. Return strict JSON only.\n\n"
        "IGNORE TERMS EXAMPLES:\n"
        "new, extra, crunchy, tasty, family pack, no artificial colours, value pack, best taste, rich in, free gift, bigger pack\n\n"
        "OUTPUT JSON:\n"
        "{\n"
        "  \"brand_name\": \"\",\n"
        "  \"product_name\": \"\",\n"
        "  \"flavor_or_variant\": \"\",\n"
        "  \"clean_display_name\": \"\",\n"
        "  \"raw_visible_name\": \"\",\n"
        "  \"ignored_marketing_text\": [],\n"
        "  \"possible_alternatives\": [],\n"
        "  \"name_confidence\": 0.0,\n"
        "  \"needs_manual_review\": false,\n"
        "  \"reason\": \"\"\n"
        "}\n\n"
        "CONFIDENCE RULES:\n"
        "- 0.90 to 1.00 = very clear visible product name\n"
        "- 0.70 to 0.89 = likely correct, acceptable for branded lookup\n"
        "- 0.50 to 0.69 = uncertain, do not trust for direct branded match\n"
        "- below 0.50 = keep visible text only, force fallback\n\n"
        "DECISION POLICY:\n"
        "- If confidence >= 0.70, branded lookup may proceed.\n"
        "- If confidence < 0.70, branded lookup should be skipped and ingredient-level analysis should be used.\n"
        "- If no clear product name exists, return the best visible text fragment and mark needs_manual_review=true.\n\n"
        "OCR TEXT:\n"
        f"{ocr_text}"
    )


def _extract_json_object(raw_text: str) -> dict[str, Any] | None:
    text = (raw_text or "").strip()
    if not text:
        return None

    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def _normalize_payload_shape(payload: dict[str, Any]) -> dict[str, Any]:
    result = {
        "brand_name": str(payload.get("brand_name") or "").strip(),
        "product_name": str(payload.get("product_name") or "").strip(),
        "flavor_or_variant": str(payload.get("flavor_or_variant") or "").strip(),
        "clean_display_name": str(payload.get("clean_display_name") or "").strip(),
        "raw_visible_name": str(payload.get("raw_visible_name") or "").strip(),
        "ignored_marketing_text": (
            payload.get("ignored_marketing_text")
            if isinstance(payload.get("ignored_marketing_text"), list)
            else []
        ),
        "possible_alternatives": (
            payload.get("possible_alternatives")
            if isinstance(payload.get("possible_alternatives"), list)
            else []
        ),
        "name_confidence": payload.get("name_confidence") if isinstance(payload.get("name_confidence"), (int, float)) else 0.0,
        "needs_manual_review": bool(payload.get("needs_manual_review", False)),
        "reason": str(payload.get("reason") or "").strip(),
    }

    if not result["clean_display_name"]:
        display_parts = [p for p in [result["product_name"], result["flavor_or_variant"]] if p]
        result["clean_display_name"] = " ".join(display_parts).strip()

    if not result["raw_visible_name"]:
        result["raw_visible_name"] = result["product_name"]

    if result["name_confidence"] < 0.70:
        result["needs_manual_review"] = True

    return result


def _gemini_request(url: str, payload: dict[str, Any]) -> requests.Response:
    return requests.post(url, json=payload, timeout=20)


async def normalize_ocr_label(ocr_text: str) -> dict[str, Any]:
    ocr_text = (ocr_text or "").strip()
    if not ocr_text:
        return _default_result(ocr_text)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _default_result(ocr_text)

    url = f"{GEMINI_API_BASE}/{GEMINI_MODEL}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": _prompt(ocr_text)}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 700
        }
    }

    try:
        response = await asyncio.to_thread(_gemini_request, url, payload)
        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates") or []
        if not candidates:
            return _default_result(ocr_text)

        content = candidates[0].get("content", {})
        parts = content.get("parts") or []
        if not parts:
            return _default_result(ocr_text)

        joined_text = "\n".join(
            part.get("text", "") for part in parts if isinstance(part, dict)
        ).strip()

        parsed = _extract_json_object(joined_text)
        if not isinstance(parsed, dict):
            return _default_result(ocr_text)

        return _normalize_payload_shape(parsed)
    except Exception:
        return _default_result(ocr_text)
