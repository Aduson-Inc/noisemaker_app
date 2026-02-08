"""
Pydantic Models for API Request/Response Validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


# ============================================================================
# AUTH MODELS
# ============================================================================

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1)
    tier: Literal['talent', 'star', 'legend', 'pending']
    # Spotify artist data (all collected from validate-artist response)
    spotify_artist_id: Optional[str] = None
    spotify_artist_name: Optional[str] = None
    spotify_artist_image_url: Optional[str] = None
    spotify_genres: Optional[List[str]] = None
    spotify_followers: Optional[int] = None
    spotify_external_url: Optional[str] = None

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    user_id: str
    token: str
    message: str = "Authentication successful"


class AuthResponseEnhanced(BaseModel):
    """Enhanced auth response with full user state for smart routing"""
    user_id: str
    token: str
    message: str = "Authentication successful"
    # User profile
    name: str = ""
    email: str = ""
    # Subscription state
    subscription_tier: Literal['pending', 'talent', 'star', 'legend'] = 'pending'
    account_status: Literal['pending', 'active', 'inactive'] = 'pending'
    # Onboarding state
    onboarding_status: str = 'tier_pending'
    onboarding_complete: bool = False
    # Milestone state (for video playback)
    pending_milestone: Optional[str] = None
    milestone_video_url: Optional[str] = None
    # Redirect hint for frontend
    redirect_to: str = '/pricing'


class MilestoneCheckResponse(BaseModel):
    milestone_reached: bool
    milestone_type: Optional[str] = None
    gender: Optional[str] = None


# ============================================================================
# OAUTH MODELS
# ============================================================================

class OAuthResponse(BaseModel):
    auth_url: str
    message: str = "Redirect user to this URL"


# ============================================================================
# OAUTH TOKEN EXCHANGE MODELS
# ============================================================================

class ExchangeTokenRequest(BaseModel):
    """Request to exchange NextAuth session for backend JWT"""
    email: EmailStr
    name: str = Field(..., min_length=1)
    provider: Literal['google', 'facebook']


class ExchangeTokenResponse(BaseModel):
    """Response with backend JWT after token exchange"""
    user_id: str
    access_token: str
    expires_in: int = 86400  # 24 hours in seconds
    token_type: str = "Bearer"


class ExchangeTokenResponseEnhanced(BaseModel):
    """Enhanced token exchange response with full user state for smart routing"""
    user_id: str
    access_token: str
    expires_in: int = 86400
    token_type: str = "Bearer"
    # User profile
    name: str = ""
    email: str = ""
    is_new_user: bool = False
    # Subscription state
    subscription_tier: Literal['pending', 'talent', 'star', 'legend'] = 'pending'
    account_status: Literal['pending', 'active', 'inactive'] = 'pending'
    # Onboarding state
    onboarding_status: str = 'tier_pending'
    onboarding_complete: bool = False
    # Milestone state
    pending_milestone: Optional[str] = None
    milestone_video_url: Optional[str] = None
    # Redirect hint
    redirect_to: str = '/pricing'


class OAuthCallbackRequest(BaseModel):
    code: str
    user_id: str
    state: str

class OAuthCallbackResponse(BaseModel):
    success: bool
    message: str
    artist_id: Optional[str] = None

class OAuthStatusResponse(BaseModel):
    connected: bool
    artist_id: Optional[str] = None


# ============================================================================
# PLATFORM MODELS
# ============================================================================

class PlatformSelectionRequest(BaseModel):
    platforms: List[str] = Field(..., min_items=1)

class PlatformConnectionStatus(BaseModel):
    name: str
    connected: bool
    quota_used: int = 0
    quota_limit: int = 100


# ============================================================================
# SONG MODELS
# ============================================================================

class SongInfo(BaseModel):
    id: str
    spotify_track_id: str
    name: str
    artist: str
    album_art: Optional[str] = None
    fire_mode: bool = False
    fire_mode_triggered: bool = False
    baseline_streams: int = 0
    current_streams: int = 0
    added_at: str

class AddSongRequest(BaseModel):
    user_id: str
    spotify_track_id: str

class AddSongResponse(BaseModel):
    success: bool
    song_id: Optional[str] = None
    message: str


# ============================================================================
# POST MODELS
# ============================================================================

class PostInfo(BaseModel):
    id: str
    song_id: str
    platform: str
    scheduled_time: str
    caption: str
    image_url: Optional[str] = None
    status: Literal['pending', 'approved', 'rejected', 'posted', 'failed']

class UpdateCaptionRequest(BaseModel):
    caption: str

class PostActionResponse(BaseModel):
    success: bool
    message: str = "Action completed"


# ============================================================================
# DASHBOARD MODELS
# ============================================================================

class DashboardStats(BaseModel):
    songs_count: int = 0
    active_posts: int = 0
    total_engagement: int = 0
    fire_mode_active: bool = False

class DashboardResponse(BaseModel):
    songs: List[SongInfo] = []
    stats: DashboardStats
    fire_mode_available: bool = False

class UserStatsResponse(BaseModel):
    monthly_listeners: int = 0
    follower_growth: int = 0
    total_streams: int = 0
    engagement_rate: float = 0.0

class PlatformStats(BaseModel):
    name: str
    engagement: int = 0
    reach: int = 0
    posts_count: int = 0


# ============================================================================
# PAYMENT MODELS
# ============================================================================

class CreateCheckoutRequest(BaseModel):
    user_id: str
    tier: Literal['talent', 'star', 'legend']

class PaymentCheckoutResponse(BaseModel):
    session_id: str
    checkout_url: str

class PaymentConfirmRequest(BaseModel):
    session_id: str

class PaymentConfirmResponse(BaseModel):
    success: bool
    message: str = "Payment confirmed"
    token: str = ""  # JWT token to restore auth after Stripe redirect


# ============================================================================
# USER MODELS
# ============================================================================

class UserProfile(BaseModel):
    user_id: str
    email: str
    artist_name: str
    subscription_tier: str
    account_status: str
    created_at: str
    spotify_connected: bool = False

class UserPreferences(BaseModel):
    timezone: str = "America/New_York"
    platforms_enabled: List[str] = []
    ai_captions_enabled: bool = True
    milestone_notifications: bool = True


# ============================================================================
# ERROR MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

class SuccessResponse(BaseModel):
    success: bool
    message: str
