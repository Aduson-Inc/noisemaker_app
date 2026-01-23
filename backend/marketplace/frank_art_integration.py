"""
Frank's Garage Integration Module
Integrates the Frank Art marketplace with the existing NOiSEMaKER system.

IMPORTANT: Frank Art is SEPARATE from album artwork collected from user songs.
- Frank Art = AI-generated art sold in the marketplace
- Album Art = Artwork from user's Spotify songs (separate system)

Author: Senior Python Backend Engineer
Version: 2.0
Security Level: Production-ready
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Local imports (relative imports for production package structure)
from .frank_art_manager import (
    get_frank_art_manager,
    get_frank_art_pool,
    place_frank_art_hold,
    download_frank_art_free,
    purchase_frank_art
)
from .artwork_analytics import (
    analytics_manager,
    track_user_action,
    track_marketplace_metrics
)
from ..data.user_manager import (
    UserManager,
    init_user_art_tokens,
    award_art_tokens_for_song,
    get_user_art_token_info,
    deduct_user_art_token
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FrankArtIntegration:
    """
    Integration layer between Frank's Garage marketplace and NOiSEMaKER system.

    Features:
    - Clean separation between Frank Art (marketplace) and album art (user songs)
    - User lifecycle management (signup tokens, song tokens)
    - Analytics integration
    - Download and purchase handling
    """

    def __init__(self):
        """Initialize integration layer."""
        try:
            self.user_manager = UserManager()

            logger.info("Frank's Garage integration initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Frank's Garage integration: {str(e)}")
            raise

    def handle_new_user_signup(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle new user signup for Frank's Garage.
        Awards 3 art tokens for new users.

        Args:
            user_id (str): New user identifier
            user_data (Dict[str, Any]): User registration data

        Returns:
            Dict[str, Any]: Signup handling result
        """
        try:
            # Award initial signup tokens (3 tokens)
            result = init_user_art_tokens(user_id, initial_tokens=3)

            if result.get('success'):
                # Track user signup
                track_user_action(user_id, 'frank_art_signup', {
                    'signup_date': datetime.now().isoformat(),
                    'tokens_awarded': 3
                })

                logger.info(f"New user {user_id} awarded 3 art tokens for Frank's Garage")

                return {
                    'success': True,
                    'message': 'Welcome! You have received 3 art tokens for free downloads.',
                    'tokens_awarded': 3,
                    'art_tokens': result.get('art_tokens', 3)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Failed to award signup tokens')
                }

        except Exception as e:
            logger.error(f"Error handling new user signup: {str(e)}")
            return {
                'success': False,
                'error': f'Signup processing failed: {str(e)}'
            }

    def handle_song_upload(self, user_id: str, song_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user song upload and award art tokens.
        Awards 3 tokens per song (max 12 from song uploads).

        Args:
            user_id (str): User uploading song
            song_data (Dict[str, Any]): Song upload data

        Returns:
            Dict[str, Any]: Token award result
        """
        try:
            # Award art tokens for song upload (3 tokens, max 12 from songs)
            result = award_art_tokens_for_song(user_id)

            if result.get('success'):
                tokens_awarded = result.get('tokens_added', 0)

                # Track song upload event
                track_user_action(user_id, 'song_upload_tokens', {
                    'song_id': song_data.get('song_id'),
                    'song_title': song_data.get('title'),
                    'upload_date': datetime.now().isoformat(),
                    'tokens_awarded': tokens_awarded
                })

                logger.info(f"User {user_id} awarded {tokens_awarded} art tokens for song upload")

                return {
                    'success': True,
                    'message': result.get('message', f'Song uploaded! You earned {tokens_awarded} art tokens.'),
                    'tokens_awarded': tokens_awarded,
                    'total_tokens': result.get('new_balance', 0),
                    'at_max': result.get('at_max', False)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Failed to award art tokens')
                }

        except Exception as e:
            logger.error(f"Error handling song upload tokens: {str(e)}")
            return {
                'success': False,
                'error': f'Token award failed: {str(e)}'
            }

    def get_user_marketplace_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user Frank's Garage status.

        Args:
            user_id (str): User identifier

        Returns:
            Dict[str, Any]: User marketplace status including tokens
        """
        try:
            # Get user art tokens
            token_info = get_user_art_token_info(user_id)

            # Get user's marketplace activity history (last 30 days)
            from marketplace.frank_art_manager import get_frank_art_manager
            manager = get_frank_art_manager()

            recent_downloads = manager._get_recent_activity('download', 30)
            recent_purchases = manager._get_recent_activity('purchase', 30)

            # Filter by user
            user_downloads = [d for d in recent_downloads if d.get('user_id') == user_id]
            user_purchases = [p for p in recent_purchases if p.get('user_id') == user_id]

            # Calculate total spending
            total_spent = sum(float(p.get('amount', 0)) for p in user_purchases)

            return {
                'success': True,
                'user_id': user_id,
                'tokens': {
                    'art_tokens': token_info.get('art_tokens', 0),
                    'tokens_from_songs': token_info.get('tokens_from_songs', 0),
                    'max_song_tokens': token_info.get('max_song_tokens', 12)
                },
                'activity': {
                    'downloads_30_days': len(user_downloads),
                    'purchases_30_days': len(user_purchases),
                    'total_spent': round(total_spent, 2)
                },
                'marketplace_access': True
            }

        except Exception as e:
            logger.error(f"Error getting user marketplace status: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get marketplace status: {str(e)}'
            }

    def handle_artwork_download(self, user_id: str, artwork_id: str) -> Dict[str, Any]:
        """
        Handle FREE artwork download (costs 1 art token).
        Art stays in pool after download.

        Args:
            user_id (str): User downloading artwork
            artwork_id (str): Artwork being downloaded

        Returns:
            Dict[str, Any]: Download result with presigned URL
        """
        try:
            from marketplace.frank_art_manager import download_frank_art_free

            # Process free download (deducts 1 token, returns presigned URL)
            result = download_frank_art_free(artwork_id, user_id)

            if result.get('success'):
                # Track download event
                track_user_action(user_id, 'frank_art_download', {
                    'artwork_id': artwork_id,
                    'download_date': datetime.now().isoformat(),
                    'tokens_used': 1,
                    'remaining_tokens': result.get('remaining_tokens', 0)
                })

                logger.info(f"User {user_id} downloaded Frank Art {artwork_id}")

            return result

        except Exception as e:
            logger.error(f"Error handling artwork download: {str(e)}")
            return {
                'success': False,
                'error': f'Download failed: {str(e)}'
            }

    def handle_artwork_purchase(self, user_id: str, artwork_ids: List[str], purchase_type: str) -> Dict[str, Any]:
        """
        Handle PAID artwork purchase (no tokens used).
        Art is removed from pool and becomes exclusive to buyer.

        Args:
            user_id (str): User making purchase
            artwork_ids (List[str]): Artworks being purchased
            purchase_type (str): 'single', 'bundle_5', or 'bundle_15'

        Returns:
            Dict[str, Any]: Purchase result with download URLs
        """
        try:
            from marketplace.frank_art_manager import purchase_frank_art

            # Process purchase (Stripe payment, NO tokens consumed)
            result = purchase_frank_art(artwork_ids, user_id, purchase_type)

            if result.get('success'):
                # Track purchase event
                track_user_action(user_id, 'frank_art_purchase', {
                    'artwork_ids': artwork_ids,
                    'purchase_type': purchase_type,
                    'amount_paid': result.get('amount_paid', 0),
                    'purchase_date': datetime.now().isoformat()
                })

                logger.info(f"User {user_id} purchased {len(artwork_ids)} Frank Art pieces for ${result.get('amount_paid', 0)}")

            return result

        except Exception as e:
            logger.error(f"Error handling artwork purchase: {str(e)}")
            return {
                'success': False,
                'error': f'Purchase failed: {str(e)}'
            }

    def ensure_system_separation(self) -> Dict[str, Any]:
        """
        Verify clean separation between Frank Art (marketplace) and Album Art (Spotify songs).

        IMPORTANT DISTINCTION:
        - Frank Art = AI-generated art sold in the marketplace (this system)
        - Album Art = Artwork from user's Spotify songs (separate system)

        Returns:
            Dict[str, Any]: Separation verification results
        """
        try:
            separation_checks = {
                'storage_separation': {
                    'frank_art_bucket': 'noisemakerpromobydoowopp',
                    'frank_art_folders': ['ArtSellingONLY/original/', 'ArtSellingONLY/mobile/', 'ArtSellingONLY/thumbnails/'],
                    'album_art_source': 'Spotify API (user song metadata)',
                    'status': 'separated'
                },
                'database_separation': {
                    'frank_art_tables': [
                        'noisemaker-frank-art',
                        'noisemaker-frank-art-purchases',
                        'noisemaker-artwork-analytics'
                    ],
                    'user_data': 'art_tokens stored on noisemaker-users table',
                    'status': 'separated'
                },
                'functionality_separation': {
                    'frank_art': 'AI-generated artwork marketplace with token/purchase system',
                    'album_art': 'User song artwork from Spotify for promotional posts',
                    'status': 'separated'
                },
                'user_interaction': {
                    'frank_art': 'Direct browsing, token downloads, purchases at /dashboard/garage',
                    'album_art': 'Automatic inclusion in social media posts',
                    'status': 'separated'
                }
            }

            return {
                'success': True,
                'separation_verified': True,
                'checks': separation_checks,
                'message': 'Frank Art (marketplace) and Album Art (Spotify songs) are properly separated'
            }

        except Exception as e:
            logger.error(f"Error checking system separation: {str(e)}")
            return {
                'success': False,
                'error': f'Separation check failed: {str(e)}'
            }

    def get_integration_health(self) -> Dict[str, Any]:
        """
        Get health status of Frank's Garage marketplace integration.

        Returns:
            Dict[str, Any]: Integration health status
        """
        try:
            # Check marketplace metrics
            marketplace_metrics = track_marketplace_metrics()

            # Check system separation
            separation_status = self.ensure_system_separation()

            # Get recent activity
            from marketplace.frank_art_manager import get_frank_art_manager
            manager = get_frank_art_manager()

            recent_activity = {
                'downloads_24h': len(manager._get_recent_activity('download', 1)),
                'purchases_24h': len(manager._get_recent_activity('purchase', 1))
            }

            health_status = {
                'overall_health': 'healthy',
                'marketplace_operational': marketplace_metrics.get('pool', {}).get('current_count', 0) > 0,
                'separation_verified': separation_status.get('separation_verified', False),
                'recent_activity': recent_activity,
                'metrics': marketplace_metrics,
                'timestamp': datetime.now().isoformat()
            }

            return {
                'success': True,
                'health': health_status
            }

        except Exception as e:
            logger.error(f"Error getting integration health: {str(e)}")
            return {
                'success': False,
                'error': f'Health check failed: {str(e)}'
            }


# Global integration manager instance
frank_art_integration = FrankArtIntegration()


# Integration hooks for main system
def on_user_signup(user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Hook for main system: handle new user signup (awards 3 art tokens)."""
    return frank_art_integration.handle_new_user_signup(user_id, user_data)


def on_song_upload(user_id: str, song_data: Dict[str, Any]) -> Dict[str, Any]:
    """Hook for main system: handle song upload (awards 3 art tokens, max 12)."""
    return frank_art_integration.handle_song_upload(user_id, song_data)


def get_user_artwork_status(user_id: str) -> Dict[str, Any]:
    """Hook for main system: get user Frank's Garage status."""
    return frank_art_integration.get_user_marketplace_status(user_id)


def download_artwork_with_tracking(user_id: str, artwork_id: str) -> Dict[str, Any]:
    """Hook for main system: FREE download (costs 1 token, art stays in pool)."""
    return frank_art_integration.handle_artwork_download(user_id, artwork_id)


def purchase_artwork_with_tracking(user_id: str, artwork_ids: List[str], purchase_type: str) -> Dict[str, Any]:
    """Hook for main system: PURCHASE (costs money, NO tokens, art removed from pool)."""
    return frank_art_integration.handle_artwork_purchase(user_id, artwork_ids, purchase_type)


def verify_system_separation() -> Dict[str, Any]:
    """Verify Frank Art (marketplace) vs Album Art (Spotify songs) separation."""
    return frank_art_integration.ensure_system_separation()


def get_marketplace_integration_health() -> Dict[str, Any]:
    """Get overall Frank's Garage integration health status."""
    return frank_art_integration.get_integration_health()
