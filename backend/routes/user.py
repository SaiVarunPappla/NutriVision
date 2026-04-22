"""
NutriVision - User Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class UserResponse(BaseModel):
    uid: str
    name: str
    email: str
    dietary_preferences: List[str] = []
    allergies: List[str] = []
    total_scans: int = 0
    created_at: str
    updated_at: str

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    dietary_preferences: Optional[List[str]] = None
    allergies: Optional[List[str]] = None

@router.get("/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    # Mock data for testing
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    return UserResponse(
        uid=user_id,
        name="Test User",
        email="test@nutrivision.com",
        dietary_preferences=["Vegan"],
        allergies=["Peanuts"],
        total_scans=5,
        created_at=now,
        updated_at=now
    )

@router.put("/user/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, update: UserProfileUpdate):
    # Mock return
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    return UserResponse(
        uid=user_id,
        name=update.name or "Test User",
        email="test@nutrivision.com",
        dietary_preferences=update.dietary_preferences or [],
        allergies=update.allergies or [],
        total_scans=5,
        created_at=now,
        updated_at=now
    )
