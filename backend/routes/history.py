"""
NutriVision - History Routes

API endpoints for managing user scan history and nutrition tracking.
"""

from fastapi import APIRouter, HTTPException
from models.recommendation import HistoryItem

router = APIRouter()


@router.get(
    "/history/{user_id}",
    response_model=list[HistoryItem],
    summary="Get Scan History",
    description="Retrieve all scan history for a specific user."
)
async def get_history(user_id: str):
    """
    Get the list of past scans for a user, ordered by most recent first.
    Used by the Android app's History screen.
    """
    # TODO: Implement Firestore query in Phase 4
    # Return empty list for now (valid response)
    return []


@router.delete(
    "/history/{history_id}",
    summary="Delete History Entry",
    description="Delete a specific scan history entry."
)
async def delete_history(history_id: str):
    """Delete a single history entry by its ID."""
    # TODO: Implement Firestore delete in Phase 4
    raise HTTPException(
        status_code=404,
        detail=f"History entry '{history_id}' not found. Implementation pending Phase 4."
    )
