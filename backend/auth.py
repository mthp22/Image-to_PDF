import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from functools import lru_cache

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)
security = HTTPBearer()


class FirebaseAuthManager:
    """Firebase authentication manager."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.firebase_initialized = False
        self.initialize()
        self._initialized = True

    def initialize(self):
        """Initialize Firebase Admin SDK."""
        try:
            firebase_creds = os.getenv("FIREBASE_CREDENTIALS_JSON")
            firebase_project = os.getenv("FIREBASE_PROJECT_ID")

            if not firebase_creds or not firebase_project:
                logger.warning("Firebase credentials not configured. Auth disabled.")
                return

            # Initialize Firebase
            if not firebase_admin._apps:
                creds = credentials.Certificate(firebase_creds)
                firebase_admin.initialize_app(creds)
            
            self.firebase_initialized = True
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            self.firebase_initialized = False

    def verify_token(self, token: str) -> dict:
        """Verify Firebase token."""
        if not self.firebase_initialized:
            logger.warning("Firebase not initialized. Skipping token verification.")
            return {"uid": "anonymous", "email": "anonymous@example.com"}

        try:
            decoded = firebase_auth.verify_id_token(token)
            return decoded
        except firebase_auth.InvalidIdTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except firebase_auth.ExpiredIdTokenError:
            raise HTTPException(status_code=401, detail="Token expired")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")

    def create_user(self, email: str, password: str) -> dict:
        """Create a new user."""
        if not self.firebase_initialized:
            raise HTTPException(status_code=503, detail="Firebase not configured")

        try:
            user = firebase_auth.create_user(email=email, password=password)
            return {
                "uid": user.uid,
                "email": user.email,
                "created": user.user_metadata.creation_timestamp,
            }
        except firebase_auth.EmailAlreadyExistsError:
            raise HTTPException(status_code=400, detail="Email already exists")
        except Exception as e:
            logger.error(f"User creation error: {e}")
            raise HTTPException(status_code=500, detail="User creation failed")

    def get_user(self, uid: str) -> dict:
        """Get user information."""
        if not self.firebase_initialized:
            raise HTTPException(status_code=503, detail="Firebase not configured")

        try:
            user = firebase_auth.get_user(uid)
            return {
                "uid": user.uid,
                "email": user.email,
                "disabled": user.disabled,
                "created": str(user.user_metadata.creation_timestamp),
            }
        except firebase_auth.UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            raise HTTPException(status_code=500, detail="Failed to get user")

    def delete_user(self, uid: str):
        """Delete a user."""
        if not self.firebase_initialized:
            raise HTTPException(status_code=503, detail="Firebase not configured")

        try:
            firebase_auth.delete_user(uid)
            return {"message": "User deleted successfully"}
        except firebase_auth.UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete user")

    def disable_user(self, uid: str):
        """Disable a user account."""
        if not self.firebase_initialized:
            raise HTTPException(status_code=503, detail="Firebase not configured")

        try:
            firebase_auth.update_user(uid, disabled=True)
            return {"message": "User disabled successfully"}
        except firebase_auth.UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            logger.error(f"Error disabling user: {e}")
            raise HTTPException(status_code=500, detail="Failed to disable user")


# Singleton instance
auth_manager = FirebaseAuthManager()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to get current user from token."""
    token = credentials.credentials
    return auth_manager.verify_token(token)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """Dependency to get optional user (auth not required)."""
    if credentials is None:
        return None
    
    token = credentials.credentials
    try:
        return auth_manager.verify_token(token)
    except HTTPException:
        return None
