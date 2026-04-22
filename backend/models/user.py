"""
NutriVision - User Models

Pydantic models for user profiles, preferences, and authentication data.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class UserCreate(BaseModel):
    """Request body for registering a new user."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "uid": "firebase_uid_123",
            "name": "John Doe",
            "email": "john@example.com",
            "dietary_preferences": ["vegetarian"],
            "allergies": ["peanuts", "gluten"]
        }
    })

    uid: str = Field(..., description="Firebase Auth UID")
    name: str = Field(..., min_length=1, description="User's display name")
    email: str = Field(..., description="User's email address")
    dietary_preferences: list[str] = Field(
        default_factory=list,
        description="Dietary preferences (e.g., vegetarian, vegan, keto)"
    )
    allergies: list[str] = Field(
        default_factory=list,
        description="Known food allergies (e.g., peanuts, gluten, dairy)"
    )


class UserUpdate(BaseModel):
    """Request body for updating user preferences."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "dietary_preferences": ["vegetarian", "gluten_free"],
            "allergies": ["peanuts", "shellfish"]
        }
    })

    name: Optional[str] = Field(None, description="Updated display name")
    dietary_preferences: Optional[list[str]] = Field(
        None, description="Updated dietary preferences"
    )
    allergies: Optional[list[str]] = Field(
        None, description="Updated allergies list"
    )


class UserResponse(BaseModel):
    """User profile returned in API responses."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "uid": "firebase_uid_123",
            "name": "John Doe",
            "email": "john@example.com",
            "dietary_preferences": ["vegetarian"],
            "allergies": ["peanuts", "gluten"],
            "total_scans": 15,
            "created_at": "2026-04-15T00:00:00Z",
            "updated_at": "2026-04-15T12:00:00Z"
        }
    })

    uid: str
    name: str
    email: str
    dietary_preferences: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    total_scans: int = Field(0, description="Total number of scans performed")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
