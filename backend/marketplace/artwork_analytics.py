"""
Frank's Garage Analytics
========================

Simplified analytics for the Frank's Garage image marketplace.
Tracks user downloads, purchases, and monitors pool levels.

Author: Tre / ADUSON Inc.
"""

import boto3
import logging
from datetime import datetime
from typing import Dict, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
AWS_REGION = 'us-east-2'
CRITICAL_POOL_THRESHOLD = 50
MAX_POOL_SIZE = 250

# Lazy-loaded AWS clients
_dynamodb = None


def get_dynamodb():
    """Lazy load DynamoDB resource."""
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    return _dynamodb


# =============================================================================
# POOL MONITORING
# =============================================================================

def get_pool_count() -> int:
    """
    Get current count of available (unpurchased) images in the pool.
    
    Returns:
        int: Number of available images
    """
    try:
        table = get_dynamodb().Table('noisemaker-frank-art')
        response = table.scan(
            Select='COUNT',
            FilterExpression='is_purchased = :false',
            ExpressionAttributeValues={':false': False}
        )
        return response.get('Count', 0)
    except Exception as e:
        logger.error(f"Error getting pool count: {e}")
        return 0


def check_pool_critical() -> bool:
    """
    Check if pool is critically low (< 50 images).
    Logs a warning if critical - no email, just CloudWatch.
    
    Returns:
        bool: True if pool is critical, False otherwise
    """
    count = get_pool_count()
    
    if count < CRITICAL_POOL_THRESHOLD:
        logger.critical(f"POOL CRITICAL: Only {count} images remaining (threshold: {CRITICAL_POOL_THRESHOLD})")
        return True
    
    logger.info(f"Pool status: {count}/{MAX_POOL_SIZE} images available")
    return False


# =============================================================================
# USER ACTION TRACKING
# =============================================================================

def track_user_action(user_id: str, action: str, artwork_id: Optional[str] = None, 
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    Track a user action (download, purchase, browse, etc.)
    
    Args:
        user_id: User identifier
        action: Action type ('download', 'purchase', 'view', etc.)
        artwork_id: Optional artwork ID if action relates to specific image
        metadata: Optional additional data
        
    Returns:
        bool: Success status
    """
    try:
        table = get_dynamodb().Table('noisemaker-user-behavior')
        
        item = {
            'behavior_id': f"{user_id}_{action}_{int(datetime.now().timestamp())}",
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        if artwork_id:
            item['artwork_id'] = artwork_id
        
        if metadata:
            item['metadata'] = metadata
            
        table.put_item(Item=item)
        logger.info(f"Tracked action: {user_id} -> {action}")
        return True
        
    except Exception as e:
        logger.error(f"Error tracking user action: {e}")
        return False


# =============================================================================
# DOWNLOAD & PURCHASE TRACKING
# =============================================================================

def track_download(user_id: str, artwork_id: str) -> bool:
    """
    Track a free download. Updates image download count and logs user action.
    Image goes back to pool after free download.
    
    Args:
        user_id: User identifier
        artwork_id: Artwork identifier
        
    Returns:
        bool: Success status
    """
    try:
        # Update download count on the artwork
        table = get_dynamodb().Table('noisemaker-frank-art')
        table.update_item(
            Key={'artwork_id': artwork_id},
            UpdateExpression='SET download_count = if_not_exists(download_count, :zero) + :one',
            ExpressionAttributeValues={
                ':zero': 0,
                ':one': 1
            }
        )
        
        # Log user action
        track_user_action(user_id, 'download', artwork_id)
        
        logger.info(f"Download tracked: {artwork_id} by {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error tracking download: {e}")
        return False


def track_purchase(user_id: str, artwork_id: str, amount: float = 0.0) -> bool:
    """
    Track an exclusive purchase. Marks image as purchased (removed from pool).
    
    Args:
        user_id: User identifier
        artwork_id: Artwork identifier
        amount: Purchase amount
        
    Returns:
        bool: Success status
    """
    try:
        # Mark artwork as purchased (exclusive)
        table = get_dynamodb().Table('noisemaker-frank-art')
        table.update_item(
            Key={'artwork_id': artwork_id},
            UpdateExpression='SET is_purchased = :true, purchased_by = :user, purchase_date = :date, purchase_amount = :amount',
            ExpressionAttributeValues={
                ':true': True,
                ':user': user_id,
                ':date': datetime.now().isoformat(),
                ':amount': str(amount)
            }
        )
        
        # Log user action
        track_user_action(user_id, 'purchase', artwork_id, {'amount': amount})
        
        # Check if pool is getting critical after purchase
        check_pool_critical()
        
        logger.info(f"Purchase tracked: {artwork_id} by {user_id} for ${amount}")
        return True
        
    except Exception as e:
        logger.error(f"Error tracking purchase: {e}")
        return False


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_artwork_stats(artwork_id: str) -> Optional[Dict[str, Any]]:
    """
    Get stats for a specific artwork.
    
    Args:
        artwork_id: Artwork identifier
        
    Returns:
        Dict with download_count, is_purchased, etc. or None if not found
    """
    try:
        table = get_dynamodb().Table('noisemaker-frank-art')
        response = table.get_item(Key={'artwork_id': artwork_id})
        
        if 'Item' in response:
            item = response['Item']
            return {
                'artwork_id': artwork_id,
                'download_count': item.get('download_count', 0),
                'is_purchased': item.get('is_purchased', False),
                'purchased_by': item.get('purchased_by'),
                'purchase_date': item.get('purchase_date')
            }
        return None
        
    except Exception as e:
        logger.error(f"Error getting artwork stats: {e}")
        return None


def get_user_history(user_id: str, limit: int = 50) -> list:
    """
    Get recent action history for a user.
    
    Args:
        user_id: User identifier
        limit: Max records to return
        
    Returns:
        List of user actions
    """
    try:
        table = get_dynamodb().Table('noisemaker-user-behavior')
        response = table.scan(
            FilterExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id},
            Limit=limit
        )
        
        actions = response.get('Items', [])
        return sorted(actions, key=lambda x: x.get('timestamp', ''), reverse=True)
        
    except Exception as e:
        logger.error(f"Error getting user history: {e}")
        return []