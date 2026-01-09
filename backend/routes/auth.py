"""
Authentication API Routes - Enhanced with Smart Routing
Includes onboarding status and milestone tracking
"""

import logging
import secrets
import os
from fastapi import APIRouter, HTTPException, status, Depends, Response
from typing import Dict, Any

from models.schemas import (
    SignUpRequest,
    SignInRequest,
    AuthResponse,
    AuthResponseEnhanced,
    MilestoneCheckResponse,
    SuccessResponse,
    ExchangeTokenRequest,
    ExchangeTokenResponse,
    ExchangeTokenResponseEnhanced
)
from middleware.auth import create_jwt_token, get_current_user_id
from auth.user_auth import UserAuth
from data.user_manager import UserManager
from data.platform_oauth_manager import PlatformOAuthManager
from data.song_manager import SongManager
from notifications.milestone_tracker import MilestoneTracker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

user_auth = UserAuth()
user_manager = UserManager()
milestone_tracker = MilestoneTracker()
platform_oauth = PlatformOAuthManager()
song_manager = SongManager()

# Platform limits by subscription tier
TIER_PLATFORM_LIMITS = {
    'talent': 2,
    'star': 5,
    'legend': 8
}

# Check if running in production (HTTPS)
IS_PRODUCTION = os.getenv('FRONTEND_URL', '').startswith('https://')


def _set_auth_cookie(response: Response, token: str) -> None:
    """
    Set the auth_token cookie with proper security attributes.

    - In production (HTTPS): HttpOnly, Secure, SameSite=Lax
    - In development (HTTP): SameSite=Lax only
    """
    cookie_options = {
        'key': 'auth_token',
        'value': token,
        'max_age': 604800,  # 7 days
        'path': '/',
        'samesite': 'lax',
    }

    if IS_PRODUCTION:
        cookie_options['httponly'] = True
        cookie_options['secure'] = True

    response.set_cookie(**cookie_options)


def _get_redirect_path(user_data: Dict, pending_milestone: Dict) -> str:
    """
    Determine where to redirect user based on their state.

    Flow: Payment → Milestone Video → HowItWorks1 → Platforms → HowItWorks2 → AddSongs → Dashboard

    Rules:
    - First-time onboarding: need at least 1 platform AND 1 song to reach dashboard
    - Once onboarding is complete: always go directly to dashboard
    - Can add more platforms/songs from dashboard (up to limits)
    """
    user_id = user_data.get('user_id')

    # 1. Check account status
    if user_data.get('account_status') == 'inactive':
        return '/account-inactive'

    # 2. Check subscription tier - must have paid
    tier = user_data.get('subscription_tier', 'pending')
    if tier == 'pending':
        return '/pricing'

    # 3. Check for pending milestone video (plays after first payment)
    if pending_milestone.get('has_pending'):
        milestone_type = pending_milestone.get('milestone_type')
        return f'/milestone/{milestone_type}'

    # 4. If onboarding already complete, go straight to dashboard
    # (User has reached dashboard before - never redirect back to onboarding)
    onboarding_status = user_data.get('onboarding_status', 'tier_pending')
    if onboarding_status == 'complete':
        return '/dashboard'

    # 5. First-time onboarding: Check platform connections (need at least 1)
    connected_count = 0

    if user_id:
        try:
            connection_status = platform_oauth.get_connection_status(user_id)
            connected_count = sum(1 for p in connection_status.values() if p.get('connected'))
        except Exception as e:
            logger.error(f"Error getting platform status for {user_id}: {e}")

    # If no platforms connected yet, go to HowItWorks1 → Platforms
    if connected_count == 0:
        return '/onboarding/how-it-works'

    # 6. First-time onboarding: Check songs (need at least 1)
    song_count = 0

    if user_id:
        try:
            user_songs = song_manager.get_user_active_songs(user_id)
            song_count = len(user_songs) if user_songs else 0
        except Exception as e:
            logger.error(f"Error getting songs for {user_id}: {e}")

    # If no songs yet, go to HowItWorks2 → AddSongs
    if song_count == 0:
        return '/onboarding/how-it-works-2'

    # 7. First-time reaching dashboard - mark onboarding complete
    if user_id and onboarding_status != 'complete':
        try:
            user_manager.update_onboarding_status(user_id, 'complete')
            logger.info(f"Onboarding completed for user {user_id}")
        except Exception as e:
            logger.error(f"Error updating onboarding status for {user_id}: {e}")

    # 8. All requirements met - go to dashboard
    return '/dashboard'


@router.post("/signup", response_model=AuthResponseEnhanced, status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest, response: Response) -> AuthResponseEnhanced:
    try:
        logger.info(f"Signup request for email: {request.email}")

        # Create user - UserAuth generates unique user_id
        user_id = user_auth.create_user(
            email=request.email,
            password=request.password,
            name=request.name,
            tier=request.tier
        )

        if not user_id:
            existing_id = user_auth.get_user_id_by_email(request.email)
            if existing_id:
                raise HTTPException(status_code=409, detail="User already exists")
            raise HTTPException(status_code=400, detail="Failed to create user")

        # Initialize user profile with all Spotify artist info
        # account_status starts as 'pending' until payment succeeds
        profile_data = {
            'subscription_tier': request.tier,
            'account_status': 'pending',  # Becomes 'active' after successful payment
            'name': request.name
        }
        # Add all Spotify fields if provided
        if request.spotify_artist_id:
            profile_data['spotify_artist_id'] = request.spotify_artist_id
        if request.spotify_artist_name:
            profile_data['spotify_artist_name'] = request.spotify_artist_name
        if request.spotify_artist_image_url:
            profile_data['spotify_artist_image_url'] = request.spotify_artist_image_url
        if request.spotify_genres:
            profile_data['spotify_genres'] = request.spotify_genres
        if request.spotify_followers is not None:
            profile_data['spotify_followers'] = request.spotify_followers
        if request.spotify_external_url:
            profile_data['spotify_external_url'] = request.spotify_external_url

        user_manager.update_user_profile(user_id, profile_data)

        # Initialize onboarding tracking
        user_manager.initialize_onboarding(user_id, 'tier_pending')

        # Initialize milestone tracking
        user_manager.initialize_milestones(user_id)

        # Initialize baseline collection
        try:
            user_manager.initialize_baseline_collection(user_id)
        except:
            pass

        # Award 3 art tokens for Frank's Garage
        try:
            user_manager.initialize_art_tokens(user_id, initial_tokens=3)
            logger.info(f"Awarded 3 art tokens to new user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to initialize art tokens: {e}")

        token = create_jwt_token(user_id)
        logger.info(f"User {user_id} created with onboarding initialized")

        # Set auth cookie with proper security (HttpOnly/Secure in production)
        _set_auth_cookie(response, token)

        return AuthResponseEnhanced(
            user_id=user_id,
            token=token,
            message="Account created successfully",
            name=request.name,
            email=request.email,
            subscription_tier=request.tier,
            account_status='pending',  # Pending until payment succeeds
            onboarding_status='tier_pending',
            onboarding_complete=False,
            pending_milestone=None,
            milestone_video_url=None,
            redirect_to='/pricing'
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


@router.post("/signin", response_model=AuthResponseEnhanced)
async def signin(request: SignInRequest, response: Response) -> AuthResponseEnhanced:
    try:
        logger.info(f"Signin request for email: {request.email}")

        user_id = user_auth.get_user_id_by_email(request.email)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not user_auth.authenticate_user(user_id, request.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_jwt_token(user_id)

        # Get full user profile for smart routing
        user_data = user_manager.get_user_profile(user_id) or {}

        # Check for pending milestones
        pending_milestone = user_manager.get_pending_milestone(user_id)

        # Determine redirect path
        redirect_to = _get_redirect_path(user_data, pending_milestone)

        onboarding_status = user_data.get('onboarding_status', 'tier_pending')

        logger.info(f"User {user_id} signed in, redirecting to {redirect_to}")

        # Set auth cookie with proper security (HttpOnly/Secure in production)
        _set_auth_cookie(response, token)

        return AuthResponseEnhanced(
            user_id=user_id,
            token=token,
            message="Signed in successfully",
            name=user_data.get('name', ''),
            email=user_data.get('email', request.email),
            subscription_tier=user_data.get('subscription_tier', 'pending'),
            account_status=user_data.get('account_status', 'active'),
            onboarding_status=onboarding_status,
            onboarding_complete=(onboarding_status == 'complete'),
            pending_milestone=pending_milestone.get('milestone_type') if pending_milestone.get('has_pending') else None,
            milestone_video_url=pending_milestone.get('video_url') if pending_milestone.get('has_pending') else None,
            redirect_to=redirect_to
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signin error: {e}")
        raise HTTPException(status_code=500, detail=f"Signin failed: {str(e)}")


@router.post("/exchange-token", response_model=ExchangeTokenResponseEnhanced)
async def exchange_token(request: ExchangeTokenRequest, response: Response) -> ExchangeTokenResponseEnhanced:
    """
    Exchange NextAuth OAuth session for backend JWT with smart routing.
    """
    try:
        logger.info(f"Token exchange for: {request.email}, provider: {request.provider}")

        user_id = user_auth.get_user_id_by_email(request.email)
        is_new_user = False

        if user_id:
            logger.info(f"Existing OAuth user: {user_id}")
        else:
            is_new_user = True
            random_password = secrets.token_urlsafe(32)

            user_id = user_auth.create_user(
                email=request.email,
                password=random_password,
                name=request.name,
                tier='pending'
            )

            if not user_id:
                raise HTTPException(status_code=500, detail="Failed to create user")

            user_manager.update_user_profile(user_id, {
                'oauth_provider': request.provider,
                'name': request.name
            })

            # Initialize onboarding and milestones for new user
            user_manager.initialize_onboarding(user_id, 'tier_pending')
            user_manager.initialize_milestones(user_id)

            # Award 3 art tokens for Frank's Garage
            try:
                user_manager.initialize_art_tokens(user_id, initial_tokens=3)
                logger.info(f"Awarded 3 art tokens to OAuth user {user_id}")
            except Exception as e:
                logger.warning(f"Failed to initialize art tokens for OAuth user: {e}")

            logger.info(f"Created OAuth user: {user_id} via {request.provider}")

        token = create_jwt_token(user_id)

        # Get user state for smart routing
        user_data = user_manager.get_user_profile(user_id) or {}
        pending_milestone = user_manager.get_pending_milestone(user_id)
        redirect_to = _get_redirect_path(user_data, pending_milestone)
        onboarding_status = user_data.get('onboarding_status', 'tier_pending')

        # Set auth cookie with proper security (HttpOnly/Secure in production)
        _set_auth_cookie(response, token)

        return ExchangeTokenResponseEnhanced(
            user_id=user_id,
            access_token=token,
            expires_in=86400,
            name=user_data.get('name', request.name),
            email=request.email,
            is_new_user=is_new_user,
            subscription_tier=user_data.get('subscription_tier', 'pending'),
            account_status=user_data.get('account_status', 'active'),
            onboarding_status=onboarding_status,
            onboarding_complete=(onboarding_status == 'complete'),
            pending_milestone=pending_milestone.get('milestone_type') if pending_milestone.get('has_pending') else None,
            milestone_video_url=pending_milestone.get('video_url') if pending_milestone.get('has_pending') else None,
            redirect_to=redirect_to
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token exchange error: {e}")
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {str(e)}")
