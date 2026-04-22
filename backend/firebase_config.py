"""
NutriVision Backend - Firebase / Firestore Initialization

Initializes the Firebase Admin SDK and provides a Firestore client.
The service account JSON key is required for server-side access.
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
from config import settings


_firestore_client = None


def initialize_firebase():
    """
    Initialize Firebase Admin SDK with service account credentials.
    Call this once during application startup.
    """
    global _firestore_client

    if firebase_admin._apps:
        # Already initialized
        _firestore_client = firestore.client()
        return

    cred_path = settings.firebase_credentials_path

    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            "projectId": settings.firebase_project_id,
        })
        _firestore_client = firestore.client()
        print(f"[Firebase] Initialized with credentials from: {cred_path}")
    else:
        # Demo mode: initialize without credentials for local development
        # Firestore operations will use mock data
        print(f"[Firebase] WARNING: Credentials file not found at '{cred_path}'")
        print("[Firebase] Running in DEMO MODE - Firestore operations will return mock data")
        _firestore_client = None


def get_firestore_client():
    """
    Get the Firestore client instance.
    Returns None if running in demo mode (no credentials).
    """
    global _firestore_client
    return _firestore_client


def is_firebase_available() -> bool:
    """Check if Firebase is initialized and available."""
    return _firestore_client is not None
