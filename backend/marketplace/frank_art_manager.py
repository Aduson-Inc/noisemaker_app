"""
Frank's Garage - Art Marketplace Manager
Manages the 250-image pool marketplace system for user downloads and purchases.
Handles artwork processing, temporary holds, and purchase transactions.

IMPORTANT: This is SEPARATE from album artwork collected from user songs.
- Frank Art = AI-generated art sold in the marketplace
- Album Art = Artwork from user's Spotify songs (separate system)

Author: Tre / ADUSON Inc.
Version: 4.0
"""

import boto3
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FrankArt:
    """Structure for Frank's Garage artwork metadata."""
    artwork_id: str
    filename: str
    upload_date: datetime
    download_count: int
    is_purchased: bool
    purchased_by: Optional[str] = None
    purchase_date: Optional[datetime] = None
    dimensions: str = "2000x2000"
    art_style: str = ""
    artist_style: str = ""
    color_scheme: str = ""


class FrankArtManager:
    """
    Frank's Garage - Art Marketplace Management System.

    Features:
    - 250-image pool with 3 size variants (2000x2000, 600x600, 200x200)
    - Temporary hold system (5-min lock while viewing)
    - Token system (3 at signup + 3 per song, max 12 from songs)
    - Download FREE with 1 token (art stays in pool)
    - Purchase system ($2.99/1, $9.99/5, $19.99/15) NO tokens, removes from pool
    - Filters: All, Popular (5+ downloads), New (7 days), Exclusive (0 downloads)
    """

    def __init__(self):
        """Initialize Frank's Garage art manager."""
        self._s3_client = None
        self._dynamodb = None

        # S3 configuration
        self.artwork_bucket = 'noisemakerpromobydoowopp'
        self.pool_original_prefix = 'ArtSellingONLY/original/'
        self.pool_mobile_prefix = 'ArtSellingONLY/mobile/'
        self.pool_thumbnail_prefix = 'ArtSellingONLY/thumbnails/'
        self.user_purchased_prefix = 'users/'
        self.sold_thumbnails_prefix = 'sold-archive/sold-thumbnails/'

        # Configuration
        self.max_pool_size = 250
        self.hold_duration_minutes = 5

        # Pricing (matches Stripe products)
        self.pricing = {
            'single': {'amount': 299, 'count': 1, 'label': '$2.99'},
            'bundle_5': {'amount': 999, 'count': 5, 'label': '$9.99'},
            'bundle_15': {'amount': 1999, 'count': 15, 'label': '$19.99'}
        }

        # Stripe price IDs
        self.stripe_prices = {
            'single': 'price_1SbCJRHIG2GktxbO3sR6LDGs',
            'bundle_5': 'price_1SbCJbHIG2GktxbOxbAlLbLK',
            'bundle_15': 'price_1SbCJwHIG2GktxbOQQaXWhVm'
        }

        logger.info("Frank's Garage art manager initialized")

    @property
    def s3_client(self):
        """Lazy load S3 client."""
        if self._s3_client is None:
            self._s3_client = boto3.client('s3', region_name='us-east-2')
        return self._s3_client

    @property
    def dynamodb(self):
        """Lazy load DynamoDB resource."""
        if self._dynamodb is None:
            self._dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        return self._dynamodb

    @property
    def artwork_table(self):
        """Frank Art pool table."""
        return self.dynamodb.Table('noisemaker-frank-art')

    @property
    def holds_table(self):
        """Artwork holds table."""
        return self.dynamodb.Table('noisemaker-artwork-holds')

    @property
    def purchases_table(self):
        """User purchases table (My Collection)."""
        return self.dynamodb.Table('noisemaker-frank-art-purchases')

    @property
    def analytics_table(self):
        """Analytics table."""
        return self.dynamodb.Table('noisemaker-artwork-analytics')

    # =========================================================================
    # POOL QUERIES (4 Tabs: All, New, Popular, Exclusive)
    # =========================================================================

    def get_artwork_pool(self, filter_type: str = 'all', user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get artwork pool with filtering options.

        Args:
            filter_type: 'all', 'new', 'popular', 'exclusive'
            user_id: User requesting the pool

        Returns:
            List of artwork with metadata and thumbnail URLs
        """
        try:
            response = self.artwork_table.scan(
                FilterExpression='is_purchased = :false',
                ExpressionAttributeValues={':false': False}
            )

            artwork_list = response.get('Items', [])

            if filter_type == 'new':
                cutoff = datetime.now() - timedelta(days=7)
                artwork_list = [
                    art for art in artwork_list
                    if datetime.fromisoformat(art.get('upload_date', '')) >= cutoff
                ]

            elif filter_type == 'popular':
                artwork_list = [
                    art for art in artwork_list
                    if art.get('download_count', 0) >= 5
                ]

            elif filter_type == 'exclusive':
                artwork_list = [
                    art for art in artwork_list
                    if art.get('download_count', 0) == 0
                ]

            for artwork in artwork_list:
                artwork['thumbnail_url'] = self._get_pool_url(artwork['artwork_id'], 'thumbnail')
                artwork['is_on_hold'] = self._check_artwork_hold(artwork['artwork_id'])

            artwork_list.sort(key=lambda x: x.get('upload_date', ''), reverse=True)

            logger.info(f"Retrieved {len(artwork_list)} artworks for filter '{filter_type}'")
            return artwork_list

        except Exception as e:
            logger.error(f"Error getting artwork pool: {e}")
            return []

    def get_pool_count(self) -> int:
        """Get current count of available artworks in pool."""
        try:
            response = self.artwork_table.scan(
                Select='COUNT',
                FilterExpression='is_purchased = :false',
                ExpressionAttributeValues={':false': False}
            )
            return response.get('Count', 0)

        except Exception as e:
            logger.error(f"Error getting pool count: {e}")
            return 0

    # =========================================================================
    # HOLDS SYSTEM (5-minute lock)
    # =========================================================================

    def place_artwork_hold(self, artwork_id: str, user_id: str) -> Dict[str, Any]:
        """Place temporary 5-minute hold on artwork for purchase consideration."""
        try:
            artwork = self._get_artwork_metadata(artwork_id)
            if not artwork or artwork.get('is_purchased', False):
                return {'success': False, 'error': 'Artwork not available'}

            existing_hold = self._get_active_hold(artwork_id)
            if existing_hold and existing_hold['user_id'] != user_id:
                return {
                    'success': False,
                    'error': 'Artwork on hold by another user',
                    'hold_expires': existing_hold['hold_expires']
                }

            session_id = str(uuid.uuid4())
            hold_start = datetime.now()
            hold_expires = hold_start + timedelta(minutes=self.hold_duration_minutes)

            self.holds_table.put_item(Item={
                'artwork_id': artwork_id,
                'user_id': user_id,
                'session_id': session_id,
                'hold_start': hold_start.isoformat(),
                'hold_expires': hold_expires.isoformat(),
                'ttl': int(hold_expires.timestamp())
            })

            logger.info(f"Hold placed: {artwork_id} for {user_id}")

            return {
                'success': True,
                'session_id': session_id,
                'hold_expires': hold_expires.isoformat(),
                'artwork': artwork
            }

        except Exception as e:
            logger.error(f"Error placing hold: {e}")
            return {'success': False, 'error': str(e)}

    def _get_active_hold(self, artwork_id: str) -> Optional[Dict[str, Any]]:
        """Check for active hold on artwork."""
        try:
            response = self.holds_table.get_item(Key={'artwork_id': artwork_id})
            hold = response.get('Item')

            if hold:
                hold_expires = datetime.fromisoformat(hold['hold_expires'])
                if hold_expires > datetime.now():
                    return hold
                else:
                    self.holds_table.delete_item(Key={'artwork_id': artwork_id})

            return None

        except Exception as e:
            logger.error(f"Error checking hold: {e}")
            return None

    def _check_artwork_hold(self, artwork_id: str) -> bool:
        """Check if artwork is currently on hold."""
        return self._get_active_hold(artwork_id) is not None

    def _release_artwork_hold(self, artwork_id: str, user_id: str):
        """Release hold on artwork."""
        try:
            self.holds_table.delete_item(Key={'artwork_id': artwork_id})
            logger.info(f"Hold released: {artwork_id}")
        except Exception as e:
            logger.error(f"Error releasing hold: {e}")

    # =========================================================================
    # FREE DOWNLOAD (1 token, art stays in pool)
    # =========================================================================

    def download_artwork(self, artwork_id: str, user_id: str) -> Dict[str, Any]:
        """
        Process FREE artwork download using 1 art token.
        Art STAYS in pool after download.
        """
        try:
            from data.user_manager import get_user_art_tokens, deduct_user_art_token

            current_tokens = get_user_art_tokens(user_id)
            if current_tokens <= 0:
                return {
                    'success': False,
                    'error': 'No art tokens available. Upload songs to earn more!',
                    'remaining_tokens': 0
                }

            artwork = self._get_artwork_metadata(artwork_id)
            if not artwork or artwork.get('is_purchased', False):
                return {'success': False, 'error': 'Artwork not available'}

            deduct_result = deduct_user_art_token(user_id)
            if not deduct_result.get('success'):
                return {'success': False, 'error': deduct_result.get('error', 'Token deduction failed')}

            download_url = self._generate_presigned_url(
                f"{self.pool_original_prefix}{artwork_id}.png"
            )

            self._increment_download_count(artwork_id)
            self._record_user_download(user_id, artwork_id, artwork)
            self._release_artwork_hold(artwork_id, user_id)
            self._log_artwork_action(artwork_id, user_id, 'download', 0.00)

            logger.info(f"Download complete: {artwork_id} by {user_id}")

            return {
                'success': True,
                'download_url': download_url,
                'artwork': artwork,
                'remaining_tokens': deduct_result.get('new_balance', current_tokens - 1)
            }

        except Exception as e:
            logger.error(f"Error processing download: {e}")
            return {'success': False, 'error': str(e)}

    def _increment_download_count(self, artwork_id: str):
        """Increment download count for artwork."""
        try:
            self.artwork_table.update_item(
                Key={'artwork_id': artwork_id},
                UpdateExpression='SET download_count = if_not_exists(download_count, :zero) + :one',
                ExpressionAttributeValues={':zero': 0, ':one': 1}
            )
        except Exception as e:
            logger.error(f"Error incrementing download count: {e}")

    def _record_user_download(self, user_id: str, artwork_id: str, artwork: Dict[str, Any]):
        """Record free download in purchases table for My Collection."""
        try:
            self.purchases_table.put_item(Item={
                'user_id': user_id,
                'artwork_id': artwork_id,
                'type': 'download',
                'thumbnail_url': self._get_pool_url(artwork_id, 'thumbnail'),
                'art_style': artwork.get('art_style', ''),
                'artist_style': artwork.get('artist_style', ''),
                'acquired_at': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error recording download: {e}")

    # =========================================================================
    # PAID PURCHASE (money, NO tokens, removes from pool)
    # =========================================================================

    def purchase_artwork(self, artwork_ids: List[str], user_id: str, purchase_type: str) -> Dict[str, Any]:
        """
        Process PAID artwork purchase. NO tokens used.
        Art is REMOVED from pool and stored in user's folder permanently.
        """
        try:
            expected_counts = {'single': 1, 'bundle_5': 5, 'bundle_15': 15}
            if len(artwork_ids) != expected_counts.get(purchase_type, 0):
                return {'success': False, 'error': f'Invalid artwork count for {purchase_type}'}

            for artwork_id in artwork_ids:
                hold = self._get_active_hold(artwork_id)
                if not hold or hold['user_id'] != user_id:
                    return {'success': False, 'error': f'Artwork {artwork_id} not held by you'}

            pricing_info = self.pricing.get(purchase_type)
            if not pricing_info:
                return {'success': False, 'error': f'Invalid purchase type'}

            amount_cents = pricing_info['amount']
            amount_dollars = amount_cents / 100

            payment_result = self._process_stripe_payment(user_id, purchase_type, artwork_ids)
            if not payment_result.get('success'):
                for artwork_id in artwork_ids:
                    self.place_artwork_hold(artwork_id, user_id)
                return {'success': False, 'error': 'Payment failed', 'details': payment_result.get('error')}

            download_urls = []
            amount_per_artwork = amount_dollars / len(artwork_ids)

            for artwork_id in artwork_ids:
                artwork = self._get_artwork_metadata(artwork_id)

                self._mark_artwork_purchased(artwork_id, user_id)

                move_success = self._move_to_purchased_folder(artwork_id, user_id)
                if not move_success:
                    logger.critical(f"PURCHASE MOVE FAILED: {artwork_id} for {user_id} - NEEDS MANUAL REVIEW")

                download_url = self._generate_purchased_download_url(artwork_id, user_id)
                download_urls.append(download_url)

                self._record_user_purchase(user_id, artwork_id, artwork, amount_per_artwork)
                self._release_artwork_hold(artwork_id, user_id)
                self._log_artwork_action(artwork_id, user_id, 'purchase', amount_per_artwork)

            logger.info(f"Purchase complete: {len(artwork_ids)} artworks by {user_id} for ${amount_dollars}")

            return {
                'success': True,
                'download_urls': download_urls,
                'purchase_type': purchase_type,
                'amount_paid': amount_dollars
            }

        except Exception as e:
            logger.error(f"Error processing purchase: {e}")
            return {'success': False, 'error': str(e)}

    def _mark_artwork_purchased(self, artwork_id: str, user_id: str):
        """Mark artwork as purchased in DynamoDB."""
        try:
            self.artwork_table.update_item(
                Key={'artwork_id': artwork_id},
                UpdateExpression='SET is_purchased = :true, purchased_by = :user, purchase_date = :date',
                ExpressionAttributeValues={
                    ':true': True,
                    ':user': user_id,
                    ':date': datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error marking purchased: {e}")
            raise

    def _move_to_purchased_folder(self, artwork_id: str, user_id: str) -> bool:
        """
        Move purchased artwork out of pool.
        
        1. Copy original (2000x2000) to users/{user_id}/purchased-art/
        2. Copy thumbnail (200x200) to sold-archive/sold-thumbnails/
        3. Verify both copies
        4. Delete all 3 sizes from pool
        
        Returns False with rollback if copy fails.
        """
        pool_original = f"ArtSellingONLY/original/{artwork_id}.png"
        pool_mobile = f"ArtSellingONLY/mobile/{artwork_id}.png"
        pool_thumbnail = f"ArtSellingONLY/thumbnails/{artwork_id}.png"

        user_original = f"users/{user_id}/purchased-art/{artwork_id}.png"
        archive_thumbnail = f"sold-archive/sold-thumbnails/{artwork_id}.png"

        copied_keys = []

        try:
            # Copy original to user folder
            self.s3_client.copy_object(
                Bucket=self.artwork_bucket,
                CopySource={'Bucket': self.artwork_bucket, 'Key': pool_original},
                Key=user_original
            )
            copied_keys.append(user_original)
            logger.info(f"Copied original to: {user_original}")

            # Copy thumbnail to archive
            self.s3_client.copy_object(
                Bucket=self.artwork_bucket,
                CopySource={'Bucket': self.artwork_bucket, 'Key': pool_thumbnail},
                Key=archive_thumbnail
            )
            copied_keys.append(archive_thumbnail)
            logger.info(f"Copied thumbnail to: {archive_thumbnail}")

            # Verify copies exist
            for key in copied_keys:
                self.s3_client.head_object(Bucket=self.artwork_bucket, Key=key)
            logger.info(f"Verified copies for {artwork_id}")

            # Delete all 3 from pool
            for pool_key in [pool_original, pool_mobile, pool_thumbnail]:
                try:
                    self.s3_client.delete_object(Bucket=self.artwork_bucket, Key=pool_key)
                    logger.info(f"Deleted from pool: {pool_key}")
                except Exception as e:
                    logger.warning(f"Could not delete {pool_key}: {e}")

            return True

        except Exception as e:
            logger.error(f"Move failed for {artwork_id}: {e}")
            logger.error(f"Rolling back {len(copied_keys)} files...")

            for key in copied_keys:
                try:
                    self.s3_client.delete_object(Bucket=self.artwork_bucket, Key=key)
                    logger.info(f"Rollback deleted: {key}")
                except Exception as rb_error:
                    logger.error(f"Rollback failed for {key}: {rb_error}")

            return False

    def _record_user_purchase(self, user_id: str, artwork_id: str, artwork: Dict[str, Any], amount: float):
        """Record paid purchase in purchases table for My Collection."""
        try:
            self.purchases_table.put_item(Item={
                'user_id': user_id,
                'artwork_id': artwork_id,
                'type': 'purchase',
                'thumbnail_url': f"https://{self.artwork_bucket}.s3.amazonaws.com/sold-archive/sold-thumbnails/{artwork_id}.png",
                's3_path': f"users/{user_id}/purchased-art/{artwork_id}.png",
                'art_style': artwork.get('art_style', '') if artwork else '',
                'artist_style': artwork.get('artist_style', '') if artwork else '',
                'amount_paid': str(amount),
                'acquired_at': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error recording purchase: {e}")

    def _process_stripe_payment(self, user_id: str, purchase_type: str, artwork_ids: List[str]) -> Dict[str, Any]:
        """Process Stripe payment for artwork purchase."""
        try:
            import stripe
            from auth.environment_loader import env_loader

            stripe_config = env_loader.get_stripe_config()
            stripe.api_key = stripe_config.get('secret_key')

            pricing_info = self.pricing.get(purchase_type)
            amount_cents = pricing_info['amount']

            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                metadata={
                    'user_id': user_id,
                    'purchase_type': purchase_type,
                    'artwork_ids': ','.join(artwork_ids),
                    'product': 'frank_art'
                },
                description=f"Frank's Garage - {purchase_type}"
            )

            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'client_secret': payment_intent.client_secret
            }

        except ImportError:
            logger.warning("Stripe not available - dev mode")
            return {'success': True, 'payment_intent_id': f"pi_dev_{int(time.time())}"}

        except Exception as e:
            logger.error(f"Stripe error: {e}")
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # USER COLLECTION (My Collection)
    # =========================================================================

    def get_user_collection(self, user_id: str) -> Dict[str, Any]:
        """Get user's downloaded and purchased artwork collection."""
        try:
            response = self.purchases_table.query(
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )

            items = response.get('Items', [])
            downloads = [i for i in items if i.get('type') == 'download']
            purchases = [i for i in items if i.get('type') == 'purchase']

            return {
                'success': True,
                'downloads': downloads,
                'purchases': purchases,
                'total_items': len(items)
            }

        except Exception as e:
            logger.error(f"Error getting collection: {e}")
            return {'success': False, 'error': str(e)}

    def get_user_tokens(self, user_id: str) -> Dict[str, Any]:
        """Get user's art token balance."""
        try:
            from data.user_manager import get_user_art_token_info
            return get_user_art_token_info(user_id)
        except Exception as e:
            logger.error(f"Error getting tokens: {e}")
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # HELPER FUNCTIONS
    # =========================================================================

    def _get_artwork_metadata(self, artwork_id: str) -> Optional[Dict[str, Any]]:
        """Get artwork metadata from DynamoDB."""
        try:
            response = self.artwork_table.get_item(Key={'artwork_id': artwork_id})
            return response.get('Item')
        except Exception as e:
            logger.error(f"Error getting metadata: {e}")
            return None

    def _get_pool_url(self, artwork_id: str, size_type: str) -> str:
        """Get public URL for pool artwork."""
        prefixes = {
            'original': self.pool_original_prefix,
            'mobile': self.pool_mobile_prefix,
            'thumbnail': self.pool_thumbnail_prefix
        }
        prefix = prefixes.get(size_type, self.pool_thumbnail_prefix)
        return f"https://{self.artwork_bucket}.s3.amazonaws.com/{prefix}{artwork_id}.png"

    def _generate_presigned_url(self, key: str, expires: int = 3600) -> str:
        """Generate presigned download URL."""
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.artwork_bucket, 'Key': key},
                ExpiresIn=expires
            )
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            return ""

    def _generate_purchased_download_url(self, artwork_id: str, user_id: str, expires: int = 86400) -> str:
        """Generate download URL for purchased artwork from user's folder."""
        key = f"users/{user_id}/purchased-art/{artwork_id}.png"
        return self._generate_presigned_url(key, expires)

    def _log_artwork_action(self, artwork_id: str, user_id: str, action: str, amount: float):
        """Log action for analytics (matches table schema: artwork_id + date)."""
        try:
            self.analytics_table.put_item(Item={
                'artwork_id': artwork_id,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'user_id': user_id,
                'action': action,
                'amount': str(amount),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error logging action: {e}")


# =============================================================================
# GLOBAL INSTANCE AND CONVENIENCE FUNCTIONS
# =============================================================================

_frank_art_manager = None


def get_frank_art_manager():
    """Get the global Frank Art manager instance."""
    global _frank_art_manager
    if _frank_art_manager is None:
        _frank_art_manager = FrankArtManager()
    return _frank_art_manager


def get_frank_art_pool(filter_type: str = 'all', user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get Frank's Garage art pool with filtering."""
    return get_frank_art_manager().get_artwork_pool(filter_type, user_id)


def place_frank_art_hold(artwork_id: str, user_id: str) -> Dict[str, Any]:
    """Place 5-minute hold on artwork."""
    return get_frank_art_manager().place_artwork_hold(artwork_id, user_id)


def download_frank_art_free(artwork_id: str, user_id: str) -> Dict[str, Any]:
    """Download artwork using 1 art token (art stays in pool)."""
    return get_frank_art_manager().download_artwork(artwork_id, user_id)


def purchase_frank_art(artwork_ids: List[str], user_id: str, purchase_type: str) -> Dict[str, Any]:
    """Purchase artwork (costs money, NO tokens, removes from pool)."""
    return get_frank_art_manager().purchase_artwork(artwork_ids, user_id, purchase_type)


def get_user_frank_art_collection(user_id: str) -> Dict[str, Any]:
    """Get user's My Collection."""
    return get_frank_art_manager().get_user_collection(user_id)