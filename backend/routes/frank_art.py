"""
Frank's Garage API Routes
Handles Frank Art marketplace operations for AI-generated artwork.

IMPORTANT: Frank Art is SEPARATE from album artwork collected from user songs.
- Frank Art = AI-generated art sold in the marketplace (this system)
- Album Art = Artwork from user's Spotify songs (separate system)
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field

# Direct imports from the actual modules
from marketplace.frank_art_manager import get_frank_art_manager
from marketplace.frank_art_integration import (
    get_user_marketplace_status,
    handle_artwork_download,
    handle_artwork_purchase,
    get_integration_health
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/frank-art", tags=["Frank's Garage"])

# Get manager instance
frank_art_manager = get_frank_art_manager()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ArtworkItem(BaseModel):
    """Artwork item in Frank's Garage"""
    artwork_id: str
    filename: str
    thumbnail_url: str
    upload_date: str
    download_count: int
    is_on_hold: bool
    can_purchase: bool
    is_exclusive: bool = Field(default=False)
    is_new: bool = Field(default=False)
    is_popular: bool = Field(default=False)
    art_style: Optional[str] = None
    artist_style: Optional[str] = None


class FrankArtResponse(BaseModel):
    """Response for artwork listing"""
    success: bool = True
    artworks: List[ArtworkItem]
    total: int
    filter: str


class UserTokensResponse(BaseModel):
    """User's art tokens for Frank's Garage"""
    success: bool = True
    user_id: str
    art_tokens: int
    tokens_from_songs: int
    max_song_tokens: int = 12


class DownloadRequest(BaseModel):
    """Request to download artwork (FREE, costs 1 token)"""
    user_id: str
    artwork_id: str


class DownloadResponse(BaseModel):
    """Response for FREE artwork download"""
    success: bool
    download_url: Optional[str] = None
    remaining_tokens: Optional[int] = None
    error: Optional[str] = None


class PurchaseRequest(BaseModel):
    """Request to purchase artwork (costs money, NO tokens)"""
    user_id: str
    artwork_ids: List[str]
    purchase_type: Literal['single', 'bundle_5', 'bundle_15']


class PurchaseResponse(BaseModel):
    """Response for artwork purchase"""
    success: bool
    download_urls: Optional[List[str]] = None
    amount_paid: Optional[float] = None
    error: Optional[str] = None


class HoldRequest(BaseModel):
    """Request to place hold on artwork"""
    user_id: str
    artwork_id: str


class HoldResponse(BaseModel):
    """Response for artwork hold"""
    success: bool
    session_id: Optional[str] = None
    hold_expires: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# FRANK'S GARAGE ENDPOINTS
# ============================================================================

@router.get("/artwork", response_model=FrankArtResponse)
async def get_frank_art(
    filter: Literal['all', 'new', 'popular', 'exclusive'] = Query('all'),
    user_id: Optional[str] = Query(None)
) -> FrankArtResponse:
    """
    Get Frank Art (AI-generated artwork) with optional filtering.

    Filters:
    - all: All available artwork
    - new: Uploaded in last 7 days
    - popular: 5+ downloads
    - exclusive: Never downloaded (0 downloads)
    """
    try:
        logger.info(f"Fetching Frank Art with filter: {filter}")

        # Get artwork pool from manager
        artworks = frank_art_manager.get_artwork_pool(filter_type=filter, user_id=user_id)

        # Transform to response format
        artwork_items = []
        for art in artworks:
            artwork_items.append(ArtworkItem(
                artwork_id=art['artwork_id'],
                filename=art['filename'],
                thumbnail_url=art.get('thumbnail_url', ''),
                upload_date=art['upload_date'],
                download_count=art['download_count'],
                is_on_hold=art.get('is_on_hold', False),
                can_purchase=art.get('can_purchase', True),
                is_exclusive=(art['download_count'] == 0),
                is_new=(filter == 'new'),
                is_popular=(art['download_count'] >= 5),
                art_style=art.get('art_style'),
                artist_style=art.get('artist_style')
            ))

        logger.info(f"Retrieved {len(artwork_items)} artworks")

        return FrankArtResponse(
            artworks=artwork_items,
            total=len(artwork_items),
            filter=filter
        )

    except Exception as e:
        logger.error(f"Error fetching Frank Art: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch artwork: {str(e)}"
        )


@router.get("/tokens", response_model=UserTokensResponse)
async def get_user_tokens(
    user_id: str = Query(..., description="User ID")
) -> UserTokensResponse:
    """
    Get user's art tokens for Frank's Garage.

    Returns:
    - art_tokens: Current token balance
    - tokens_from_songs: Tokens earned from song uploads
    - max_song_tokens: Maximum tokens earnable from songs (12)
    """
    try:
        logger.info(f"Fetching tokens for user: {user_id}")

        # Get status from integration
        status_result = get_user_marketplace_status(user_id)

        if not status_result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=status_result.get('error', 'Failed to get tokens')
            )

        tokens = status_result.get('tokens', {})

        return UserTokensResponse(
            user_id=user_id,
            art_tokens=tokens.get('art_tokens', 0),
            tokens_from_songs=tokens.get('tokens_from_songs', 0),
            max_song_tokens=tokens.get('max_song_tokens', 12)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user tokens: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tokens: {str(e)}"
        )


@router.post("/hold", response_model=HoldResponse)
async def place_artwork_hold(request: HoldRequest) -> HoldResponse:
    """
    Place temporary hold on artwork for purchase consideration.

    Hold lasts 5 minutes and prevents other users from purchasing.
    """
    try:
        logger.info(f"Placing hold on artwork {request.artwork_id} for user {request.user_id}")

        # Place hold
        result = frank_art_manager.place_artwork_hold(request.artwork_id, request.user_id)

        if not result.get('success'):
            return HoldResponse(
                success=False,
                error=result.get('error', 'Failed to place hold')
            )

        return HoldResponse(
            success=True,
            session_id=result.get('session_id'),
            hold_expires=result.get('hold_expires')
        )

    except Exception as e:
        logger.error(f"Error placing artwork hold: {str(e)}")
        return HoldResponse(
            success=False,
            error=str(e)
        )


@router.post("/download", response_model=DownloadResponse)
async def download_frank_art(request: DownloadRequest) -> DownloadResponse:
    """
    Download artwork using art tokens (FREE download).

    Requirements:
    - User must have at least 1 art token
    - Artwork must not be purchased by another user
    - Costs 1 token per download
    - Artwork STAYS in pool after free download (others can still get it)
    """
    try:
        logger.info(f"Processing FREE download for artwork {request.artwork_id} by user {request.user_id}")

        # Process download with integrated tracking
        result = handle_artwork_download(
            request.user_id,
            request.artwork_id
        )

        if not result.get('success'):
            return DownloadResponse(
                success=False,
                error=result.get('error', 'Download failed')
            )

        return DownloadResponse(
            success=True,
            download_url=result.get('download_url'),
            remaining_tokens=result.get('remaining_tokens')
        )

    except Exception as e:
        logger.error(f"Error processing download: {str(e)}")
        return DownloadResponse(
            success=False,
            error=str(e)
        )


@router.post("/purchase", response_model=PurchaseResponse)
async def purchase_frank_art(request: PurchaseRequest) -> PurchaseResponse:
    """
    Purchase artwork for exclusive ownership (PAID, no tokens used).

    Purchase removes artwork from pool IMMEDIATELY and provides exclusive download.

    Pricing:
    - single: $2.99 (1 artwork)
    - bundle_5: $9.99 (5 artworks)
    - bundle_15: $19.99 (15 artworks)

    Requirements:
    - Artwork must be on hold by requesting user
    - Valid Stripe payment required
    - NO tokens required or consumed
    - Purchased artwork removed from pool IMMEDIATELY
    - Moved to sold-archive/ for weekly cleanup
    """
    try:
        logger.info(f"Processing PURCHASE for {len(request.artwork_ids)} artworks by user {request.user_id}")

        # Process purchase with integrated tracking
        result = handle_artwork_purchase(
            request.user_id,
            request.artwork_ids,
            request.purchase_type
        )

        if not result.get('success'):
            return PurchaseResponse(
                success=False,
                error=result.get('error', 'Purchase failed')
            )

        return PurchaseResponse(
            success=True,
            download_urls=result.get('download_urls'),
            amount_paid=result.get('amount_paid')
        )

    except Exception as e:
        logger.error(f"Error processing purchase: {str(e)}")
        return PurchaseResponse(
            success=False,
            error=str(e)
        )


@router.get("/analytics")
async def get_frank_art_analytics() -> Dict[str, Any]:
    """
    Get Frank's Garage analytics (admin/monitoring).

    Returns pool status, activity metrics, and system health.
    """
    try:
        logger.info("Fetching Frank's Garage analytics")

        # Get basic analytics from manager
        pool_count = frank_art_manager.get_pool_count()
        
        analytics = {
            'pool_count': pool_count,
            'max_pool_size': frank_art_manager.max_pool_size,
            'pool_percentage': round((pool_count / frank_art_manager.max_pool_size) * 100, 1)
        }

        return {
            "success": True,
            "analytics": analytics
        }

    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics: {str(e)}"
        )


@router.get("/health")
async def frank_art_health_check() -> Dict[str, Any]:
    """
    Health check for Frank's Garage integration.

    Verifies marketplace is operational and properly integrated.
    """
    try:
        # Get integration health
        health = get_integration_health()

        return health

    except Exception as e:
        logger.error(f"Frank's Garage health check failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "overall_health": "unhealthy"
        }


logger.info("Frank's Garage routes initialized")