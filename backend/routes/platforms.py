"""
Platform OAuth API Routes
Handles OAuth for 8 social media platforms: Instagram, Twitter, Facebook,
YouTube, TikTok, Reddit, Discord, Threads
"""

import logging
import os
from fastapi import APIRouter, HTTPException, status, Query, Depends

from models.schemas import (
    OAuthResponse,
    OAuthCallbackRequest,
    OAuthCallbackResponse,
    PlatformSelectionRequest,
    SuccessResponse
)
from middleware.auth import get_current_user_id
from data.platform_oauth_manager import PlatformOAuthManager
from data.user_manager import user_manager

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/oauth", tags=["Platform OAuth"])

# Initialize platform OAuth manager
platform_oauth = PlatformOAuthManager()

# Supported platforms
SUPPORTED_PLATFORMS = ['instagram', 'twitter', 'facebook', 'youtube', 'tiktok', 'reddit', 'discord', 'threads']

# Frontend URL for OAuth redirects
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')


@router.get("/{platform}/connect", response_model=OAuthResponse)
async def get_platform_auth_url(
    platform: str,
    user_id: str = Query(..., description="User ID requesting platform connection")
) -> OAuthResponse:
    """
    Get OAuth authorization URL for a platform.

    Supports: instagram, twitter, facebook, youtube, tiktok, reddit, discord, threads
    """
    try:
        # Validate platform
        if platform not in SUPPORTED_PLATFORMS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}. Supported platforms: {', '.join(SUPPORTED_PLATFORMS)}"
            )

        logger.info(f"Generating {platform} auth URL for user: {user_id}")

        # Generate redirect URI (this should match your frontend callback route)
        redirect_uri = f"{FRONTEND_URL}/onboarding/platforms/callback/{platform}"

        # Initiate OAuth flow
        oauth_result = platform_oauth.initiate_oauth(
            user_id=user_id,
            platform=platform,
            redirect_uri=redirect_uri
        )

        if not oauth_result.get('auth_url'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate authorization URL for {platform}"
            )

        return OAuthResponse(
            auth_url=oauth_result['auth_url'],
            message=f"Redirect user to authorize {platform}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating {platform} auth URL for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate authorization URL: {str(e)}"
        )


@router.post("/{platform}/callback", response_model=OAuthCallbackResponse)
async def handle_platform_callback(
    platform: str,
    request: OAuthCallbackRequest
) -> OAuthCallbackResponse:
    """
    Handle OAuth callback from platform.

    Exchanges authorization code for access tokens and stores them.
    """
    try:
        # Validate platform
        if platform not in SUPPORTED_PLATFORMS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}"
            )

        logger.info(f"Handling {platform} callback for user: {request.user_id}")

        # Generate redirect URI (must match the one used in initiate_oauth)
        redirect_uri = f"{FRONTEND_URL}/onboarding/platforms/callback/{platform}"

        # Handle OAuth callback
        callback_result = platform_oauth.handle_callback(
            user_id=request.user_id,
            platform=platform,
            code=request.code,
            redirect_uri=redirect_uri,
            state=None  # State validation handled internally
        )

        if not callback_result.get('success'):
            error_message = callback_result.get('error', 'Failed to connect platform')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        logger.info(f"{platform} connected successfully for user {request.user_id}")

        return OAuthCallbackResponse(
            success=True,
            message=f"{platform.title()} connected successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling {platform} callback for {request.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect {platform}: {str(e)}"
        )


@router.get("/{platform}/status")
async def check_platform_status(
    platform: str,
    user_id: str = Query(..., description="User ID to check connection")
):
    """
    Check if a specific platform is connected for user.

    Returns connection status for the platform.
    """
    try:
        # Validate platform
        if platform not in SUPPORTED_PLATFORMS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}"
            )

        logger.info(f"Checking {platform} status for user: {user_id}")

        # Get platform token
        token_data = platform_oauth.get_user_token(user_id, platform)

        return {
            "connected": bool(token_data),
            "platform": platform
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking {platform} status for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check {platform} connection status"
        )


# User platform management endpoints
user_router = APIRouter(prefix="/api/user", tags=["User Platforms"])


@user_router.post("/{user_id}/platforms", response_model=SuccessResponse)
async def save_user_platforms(
    user_id: str,
    request: PlatformSelectionRequest,
    current_user_id: str = Depends(get_current_user_id)
) -> SuccessResponse:
    """
    Save user's selected platforms.

    User selects which platforms they want to use for posting.
    """
    try:
        # Verify user can only update their own platforms
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update other user's platforms"
            )

        logger.info(f"Saving platform selection for user: {user_id}")

        # Validate platforms
        invalid_platforms = [p for p in request.platforms if p not in SUPPORTED_PLATFORMS]
        if invalid_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platforms: {', '.join(invalid_platforms)}"
            )

        # Save platform selection using user_manager
        result = user_manager.set_user_platform_selection(user_id, request.platforms)

        if not result.get('success'):
            error_message = result.get('error', 'Failed to save platform selection')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        return SuccessResponse(
            success=True,
            message=f"Platform selection saved: {', '.join(request.platforms)}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving platforms for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save platform selection"
        )


@user_router.get("/{user_id}/platforms/status")
async def get_platforms_status(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get connection status for all platforms for a user.

    Returns which platforms are connected and their OAuth status.
    """
    try:
        # Verify user can only check their own status
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other user's platform status"
            )

        logger.info(f"Getting platform status for user: {user_id}")

        # Get connection status from platform OAuth manager
        connection_status = platform_oauth.get_connection_status(user_id)

        # Get user's selected platforms
        platform_selection = user_manager.get_user_platform_selection(user_id)

        return {
            "connections": connection_status,
            "selected_platforms": platform_selection.get('platforms_enabled', []),
            "platform_limit": platform_selection.get('platform_limit', 3),
            "subscription_tier": platform_selection.get('subscription_tier', 'talent')
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting platform status for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get platform status"
        )


# Include both routers
def get_routers():
    """Return both platform OAuth router and user platforms router."""
    return [router, user_router]
