"""
Frank's Garage Integration Module
Connects Frank Art marketplace to noisemaker user system.

- Awards tokens on signup (3 tokens)
- Awards tokens on song upload (3 per song, max 12 from songs)
- Handles downloads and purchases with tracking

Author: Tre / ADUSON Inc.
Version: 2.0
"""

import logging
from datetime import datetime
from typing import Dict, List, Any

# Local imports - use absolute imports
from marketplace.frank_art_manager import (
    get_frank_art_manager,
    download_frank_art_free,
    purchase_frank_art
)
from marketplace.artwork_analytics import track_user_action
from data.user_manager import (
    init_user_art_tokens,
    award_art_tokens_for_song,
    get_user_art_token_info
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# TOKEN MANAGEMENT
# =============================================================================

def on_user_signup(user_id: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Handle new user signup - awards 3 art tokens.
    
    Args:
        user_id: New user identifier
        user_data: Optional user registration data
        
    Returns:
        Result with tokens awarded
    """
    try:
        result = init_user_art_tokens(user_id, initial_tokens=3)
        
        if result.get('success'):
            track_user_action(user_id, 'signup', metadata={'tokens_awarded': 3})
            logger.info(f"Signup tokens awarded: {user_id} got 3 tokens")
            
            return {
                'success': True,
                'tokens_awarded': 3,
                'total_tokens': result.get('art_tokens', 3)
            }
        
        return {'success': False, 'error': result.get('error', 'Token init failed')}
        
    except Exception as e:
        logger.error(f"Signup token error: {e}")
        return {'success': False, 'error': str(e)}


def on_song_upload(user_id: str, song_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Handle song upload - awards 3 art tokens (max 12 from songs).
    
    Args:
        user_id: User uploading song
        song_data: Optional song data
        
    Returns:
        Result with tokens awarded
    """
    try:
        result = award_art_tokens_for_song(user_id)
        
        if result.get('success'):
            tokens_awarded = result.get('tokens_added', 0)
            
            track_user_action(user_id, 'song_upload', metadata={
                'song_id': song_data.get('song_id') if song_data else None,
                'tokens_awarded': tokens_awarded
            })
            
            logger.info(f"Song upload tokens: {user_id} got {tokens_awarded}")
            
            return {
                'success': True,
                'tokens_awarded': tokens_awarded,
                'total_tokens': result.get('new_balance', 0),
                'at_max': result.get('at_max', False)
            }
        
        return {'success': False, 'error': result.get('error', 'Token award failed')}
        
    except Exception as e:
        logger.error(f"Song upload token error: {e}")
        return {'success': False, 'error': str(e)}


def get_user_tokens(user_id: str) -> Dict[str, Any]:
    """
    Get user's art token balance.
    
    Args:
        user_id: User identifier
        
    Returns:
        Token info
    """
    try:
        return get_user_art_token_info(user_id)
    except Exception as e:
        logger.error(f"Get tokens error: {e}")
        return {'success': False, 'error': str(e)}


# =============================================================================
# DOWNLOAD & PURCHASE HANDLERS
# =============================================================================

def handle_artwork_download(user_id: str, artwork_id: str) -> Dict[str, Any]:
    """
    Handle FREE artwork download (costs 1 token, art stays in pool).
    
    Args:
        user_id: User downloading
        artwork_id: Artwork to download
        
    Returns:
        Download result with presigned URL
    """
    try:
        result = download_frank_art_free(artwork_id, user_id)
        
        if result.get('success'):
            track_user_action(user_id, 'download', artwork_id, metadata={
                'tokens_used': 1,
                'remaining': result.get('remaining_tokens', 0)
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        return {'success': False, 'error': str(e)}


def handle_artwork_purchase(user_id: str, artwork_ids: List[str], purchase_type: str) -> Dict[str, Any]:
    """
    Handle PAID artwork purchase (costs money, NO tokens, removes from pool).
    
    Args:
        user_id: User purchasing
        artwork_ids: List of artwork IDs
        purchase_type: 'single', 'bundle_5', 'bundle_15'
        
    Returns:
        Purchase result with download URLs
    """
    try:
        result = purchase_frank_art(artwork_ids, user_id, purchase_type)
        
        if result.get('success'):
            track_user_action(user_id, 'purchase', metadata={
                'artwork_ids': artwork_ids,
                'purchase_type': purchase_type,
                'amount': result.get('amount_paid', 0)
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Purchase error: {e}")
        return {'success': False, 'error': str(e)}


# =============================================================================
# USER COLLECTION
# =============================================================================

def get_user_collection(user_id: str) -> Dict[str, Any]:
    """
    Get user's My Collection (downloads and purchases).
    
    Args:
        user_id: User identifier
        
    Returns:
        Collection data
    """
    try:
        return get_frank_art_manager().get_user_collection(user_id)
    except Exception as e:
        logger.error(f"Collection error: {e}")
        return {'success': False, 'error': str(e)}


# =============================================================================
# STATUS & HEALTH (used by routes)
# =============================================================================

def get_user_marketplace_status(user_id: str) -> Dict[str, Any]:
    """
    Get user's marketplace status including tokens.
    
    Args:
        user_id: User identifier
        
    Returns:
        Status with token info
    """
    try:
        token_info = get_user_art_token_info(user_id)
        
        return {
            'success': True,
            'tokens': {
                'art_tokens': token_info.get('art_tokens', 0),
                'tokens_from_songs': token_info.get('tokens_from_songs', 0),
                'max_song_tokens': 12
            }
        }
    except Exception as e:
        logger.error(f"Status error: {e}")
        return {'success': False, 'error': str(e)}


def get_integration_health() -> Dict[str, Any]:
    """
    Health check for Frank's Garage integration.
    
    Returns:
        Health status
    """
    try:
        from marketplace.artwork_analytics import get_pool_count
        
        pool_count = get_pool_count()
        
        return {
            'success': True,
            'overall_health': 'healthy' if pool_count > 50 else 'warning',
            'pool_count': pool_count,
            'pool_status': 'ok' if pool_count > 50 else 'low'
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            'success': False,
            'error': str(e),
            'overall_health': 'unhealthy'
        }


# =============================================================================
# CONVENIENCE ALIASES
# =============================================================================

# These match what other parts of the system might call
download_artwork_with_tracking = handle_artwork_download
purchase_artwork_with_tracking = handle_artwork_purchase
get_user_artwork_status = get_user_tokens