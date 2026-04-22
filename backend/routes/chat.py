"""
NutriVision - Chat Routes

API endpoint for AI chat assistant.
"""

from fastapi import APIRouter
from models.chat import ChatRequest, ChatResponse
from services.chat_service import generate_chat_answer


router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask NutriVision AI",
    description="Ask a question with optional scan-result context."
)
async def ask_chat(request: ChatRequest):
    answer, source = await generate_chat_answer(
        request.question,
        request.scan_context,
        request.user_profile,
    )
    return ChatResponse(
        answer=answer,
        source=source,
        used_scan_context=bool(request.scan_context),
    )
