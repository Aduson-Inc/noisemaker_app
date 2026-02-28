"""
JWT Authentication Middleware
Handles token creation, validation, and user authentication
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Import environment loader for Parameter Store access
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.environment_loader import env_loader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration - Load from Parameter Store
# Using app-level parameter for JWT secret
JWT_SECRET = env_loader.get_jwt_secret()
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Security scheme
security = HTTPBearer()


def create_jwt_token(user_id: str, name: str = "", email: str = "") -> str:
    """
    Create JWT token for authenticated user.

    Args:
        user_id (str): User identifier
        name (str): User display name
        email (str): User email

    Returns:
        str: JWT token
    """
    try:
        expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)

        payload = {
            'user_id': user_id,
            'sub': user_id,
            'name': name,
            'email': email,
            'exp': expiration,
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        logger.info(f"Created JWT token for user {user_id}")

        return token

    except Exception as e:
        logger.error(f"Error creating JWT token: {e}")
        raise


def verify_jwt_token(token: str) -> Optional[str]:
    """
    Verify JWT token and extract user_id.

    Args:
        token (str): JWT token

    Returns:
        Optional[str]: User ID if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')

        if not user_id:
            logger.warning("JWT token missing user_id")
            return None

        return user_id

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verifying JWT token: {e}")
        return None


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency to extract and validate user_id from JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        str: Validated user ID

    Raises:
        HTTPException: If token is invalid or missing
    """
    try:
        token = credentials.credentials
        user_id = verify_jwt_token(token)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return user_id

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_current_user(
    user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    FastAPI dependency to get current user information.
    Can be extended to fetch user profile from database.

    Args:
        user_id: Validated user ID from token

    Returns:
        dict: User information
    """
    return {
        'user_id': user_id
    }


# Optional: Create a version that doesn't raise exceptions for optional auth
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """
    Optional authentication - returns None if no token provided.
    Useful for endpoints that work with or without authentication.

    Args:
        credentials: Optional HTTP authorization credentials

    Returns:
        Optional[str]: User ID if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        return verify_jwt_token(token)
    except Exception:
        return None
