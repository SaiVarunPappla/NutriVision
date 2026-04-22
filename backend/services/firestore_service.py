"""
NutriVision - Firestore Service

Handles all Firebase Firestore CRUD operations for:
- Users, Scans, Ingredients, Nutrition Results, Recommendations, History

This service abstracts Firestore so that route handlers don't interact
with the database directly. Falls back to in-memory storage in demo mode.
"""

from typing import Optional
from datetime import datetime, timezone
from firebase_config import get_firestore_client, is_firebase_available


# In-memory store for demo mode (when Firebase is not configured)
_demo_store = {
    "users": {},
    "scans": {},
    "nutrition_results": {},
    "recommendations": {},
    "history": {},
}


def _now_iso() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


# ========================
# USER OPERATIONS
# ========================

async def create_user(user_data: dict) -> dict:
    """Create a new user document in the 'users' collection."""
    db = get_firestore_client()
    user_data["created_at"] = _now_iso()
    user_data["updated_at"] = _now_iso()
    user_data["total_scans"] = 0

    if db:
        doc_ref = db.collection("users").document(user_data["uid"])
        doc_ref.set(user_data)
    else:
        _demo_store["users"][user_data["uid"]] = user_data

    return user_data


async def get_user(user_id: str) -> Optional[dict]:
    """Retrieve a user document by UID."""
    db = get_firestore_client()

    if db:
        doc = db.collection("users").document(user_id).get()
        return doc.to_dict() if doc.exists else None
    else:
        return _demo_store["users"].get(user_id)


async def update_user(user_id: str, update_data: dict) -> Optional[dict]:
    """Update fields on an existing user document."""
    db = get_firestore_client()
    update_data["updated_at"] = _now_iso()

    if db:
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        doc_ref.update(update_data)
        return doc_ref.get().to_dict()
    else:
        if user_id not in _demo_store["users"]:
            return None
        _demo_store["users"][user_id].update(update_data)
        return _demo_store["users"][user_id]


# ========================
# SCAN OPERATIONS
# ========================

async def create_scan(scan_data: dict) -> dict:
    """Create a new scan document in the 'scans' collection."""
    db = get_firestore_client()
    scan_data["created_at"] = _now_iso()

    if db:
        doc_ref = db.collection("scans").document(scan_data["scan_id"])
        doc_ref.set(scan_data)
    else:
        _demo_store["scans"][scan_data["scan_id"]] = scan_data

    return scan_data


async def get_scan(scan_id: str) -> Optional[dict]:
    """Retrieve a scan document by scan_id."""
    db = get_firestore_client()

    if db:
        doc = db.collection("scans").document(scan_id).get()
        return doc.to_dict() if doc.exists else None
    else:
        return _demo_store["scans"].get(scan_id)


async def update_scan_status(scan_id: str, status: str):
    """Update the status of a scan (processing → completed/failed)."""
    db = get_firestore_client()

    if db:
        db.collection("scans").document(scan_id).update({"status": status})
    else:
        if scan_id in _demo_store["scans"]:
            _demo_store["scans"][scan_id]["status"] = status


# ========================
# NUTRITION RESULT OPERATIONS
# ========================

async def save_nutrition_result(result_data: dict) -> dict:
    """Save a nutrition analysis result to the 'nutrition_results' collection."""
    db = get_firestore_client()
    result_data["created_at"] = _now_iso()

    if db:
        doc_ref = db.collection("nutrition_results").document(result_data["result_id"])
        doc_ref.set(result_data)
    else:
        _demo_store["nutrition_results"][result_data["result_id"]] = result_data

    return result_data


async def get_nutrition_result(scan_id: str) -> Optional[dict]:
    """Retrieve nutrition results for a specific scan."""
    db = get_firestore_client()

    if db:
        results = db.collection("nutrition_results") \
            .where("scan_id", "==", scan_id) \
            .limit(1) \
            .get()
        return results[0].to_dict() if results else None
    else:
        for result in _demo_store["nutrition_results"].values():
            if result.get("scan_id") == scan_id:
                return result
        return None


# ========================
# RECOMMENDATION OPERATIONS
# ========================

async def save_recommendations(rec_data: dict) -> dict:
    """Save recommendations for a scan to the 'recommendations' collection."""
    db = get_firestore_client()
    rec_data["created_at"] = _now_iso()

    if db:
        doc_ref = db.collection("recommendations").document(rec_data["recommendation_id"])
        doc_ref.set(rec_data)
    else:
        _demo_store["recommendations"][rec_data["recommendation_id"]] = rec_data

    return rec_data


# ========================
# HISTORY OPERATIONS
# ========================

async def save_history_entry(history_data: dict) -> dict:
    """Save a scan history entry to the 'history' collection."""
    db = get_firestore_client()
    history_data["created_at"] = _now_iso()

    if db:
        doc_ref = db.collection("history").document(history_data["history_id"])
        doc_ref.set(history_data)
    else:
        _demo_store["history"][history_data["history_id"]] = history_data

    return history_data


async def get_user_history(user_id: str) -> list[dict]:
    """Retrieve all history entries for a user, ordered by most recent."""
    db = get_firestore_client()

    if db:
        results = db.collection("history") \
            .where("user_id", "==", user_id) \
            .order_by("created_at", direction="DESCENDING") \
            .limit(50) \
            .get()
        return [doc.to_dict() for doc in results]
    else:
        entries = [
            v for v in _demo_store["history"].values()
            if v.get("user_id") == user_id
        ]
        return sorted(entries, key=lambda x: x.get("created_at", ""), reverse=True)


async def delete_history_entry(history_id: str) -> bool:
    """Delete a history entry. Returns True if deleted, False if not found."""
    db = get_firestore_client()

    if db:
        doc_ref = db.collection("history").document(history_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            return True
        return False
    else:
        if history_id in _demo_store["history"]:
            del _demo_store["history"][history_id]
            return True
        return False


async def increment_user_scan_count(user_id: str):
    """Increment the total_scans counter for a user."""
    db = get_firestore_client()

    if db:
        from google.cloud.firestore_v1 import Increment
        db.collection("users").document(user_id).update({
            "total_scans": Increment(1)
        })
    else:
        if user_id in _demo_store["users"]:
            _demo_store["users"][user_id]["total_scans"] = \
                _demo_store["users"][user_id].get("total_scans", 0) + 1
