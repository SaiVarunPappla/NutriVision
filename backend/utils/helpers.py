"""
NutriVision - Helper Utilities

Common helper functions used across the backend.
"""

import uuid
from datetime import datetime, timezone


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID with an optional prefix.

    Args:
        prefix: Optional prefix (e.g., "scan", "rec", "hist")

    Returns:
        Unique ID string like "scan_a1b2c3d4"
    """
    short_id = uuid.uuid4().hex[:8]
    if prefix:
        return f"{prefix}_{short_id}"
    return short_id


def now_iso() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def calculate_daily_pct(value: float, daily_value: float) -> float:
    """
    Calculate the percentage of daily recommended value.

    Args:
        value: Nutrient amount
        daily_value: Daily recommended value for that nutrient

    Returns:
        Percentage rounded to 1 decimal place
    """
    if daily_value <= 0:
        return 0.0
    return round((value / daily_value) * 100, 1)


def safe_float(value, default: float = 0.0) -> float:
    """Safely convert a value to float, returning default on failure."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to a maximum length, adding ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
