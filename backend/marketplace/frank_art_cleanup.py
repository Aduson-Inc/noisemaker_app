"""
Frank's Garage - Weekly Cleanup Job
====================================

Runs weekly (Mondays via EventBridge) to:
1. Delete purchased artwork files older than 3 days (user already has their copy)
2. Recycle old unpurchased pool images to content-colortemplates for reuse

Author: Tre / ADUSON Inc.
Version: 2.0
"""

import boto3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
AWS_REGION = 'us-east-2'
S3_BUCKET = 'noisemakerpromobydoowopp'
CLEANUP_DAYS = 3
MAX_POOL_SIZE = 250

# S3 paths
POOL_ORIGINAL = 'ArtSellingONLY/original/'
POOL_MOBILE = 'ArtSellingONLY/mobile/'
POOL_THUMBNAIL = 'ArtSellingONLY/thumbnails/'
SOLD_THUMBNAILS = 'sold-archive/sold-thumbnails/'
COLOR_TEMPLATES = 'content-colortemplates/'

# Color mapping for recycled images
COLOR_FOLDERS = ['blue', 'green', 'neutral', 'orange', 'pink', 'purple', 'red', 'yellow']
SHADE_FOLDERS = ['dark', 'normal', 'light']  # neutral only has dark/light


# =============================================================================
# COLOR ANALYSIS (for recycling old pool images)
# =============================================================================

def analyze_image_color(image_bytes: bytes) -> Tuple[str, str]:
    """
    Analyze image and return (color, shade) for content-colortemplates folder.
    
    Returns:
        Tuple of (color_folder, shade_folder) e.g. ('blue', 'dark')
    """
    try:
        from PIL import Image
        import io
        
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert('RGB')
        image = image.resize((100, 100))  # Small sample for speed
        
        pixels = list(image.getdata())
        total_pixels = len(pixels)
        
        # Calculate average RGB
        avg_r = sum(p[0] for p in pixels) // total_pixels
        avg_g = sum(p[1] for p in pixels) // total_pixels
        avg_b = sum(p[2] for p in pixels) // total_pixels
        
        # Determine color
        color = _classify_color(avg_r, avg_g, avg_b)
        
        # Determine shade based on brightness
        brightness = (avg_r + avg_g + avg_b) / 3
        shade = _classify_shade(brightness, color)
        
        return color, shade
        
    except Exception as e:
        logger.error(f"Color analysis failed: {e}")
        return 'neutral', 'normal'


def _classify_color(r: int, g: int, b: int) -> str:
    """Classify RGB values into one of 8 color folders."""
    
    # Check for neutral (low saturation)
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    saturation = (max_val - min_val) / max_val if max_val > 0 else 0
    
    if saturation < 0.15:
        return 'neutral'
    
    # Calculate hue
    if max_val == min_val:
        hue = 0
    elif max_val == r:
        hue = 60 * ((g - b) / (max_val - min_val) % 6)
    elif max_val == g:
        hue = 60 * ((b - r) / (max_val - min_val) + 2)
    else:
        hue = 60 * ((r - g) / (max_val - min_val) + 4)
    
    if hue < 0:
        hue += 360
    
    # Map hue to color folder
    if hue < 15 or hue >= 345:
        return 'red'
    elif hue < 45:
        return 'orange'
    elif hue < 75:
        return 'yellow'
    elif hue < 165:
        return 'green'
    elif hue < 255:
        return 'blue'
    elif hue < 285:
        return 'purple'
    elif hue < 345:
        return 'pink'
    
    return 'neutral'


def _classify_shade(brightness: float, color: str) -> str:
    """Classify brightness into shade folder."""
    
    # Neutral only has dark and light (no normal)
    if color == 'neutral':
        return 'dark' if brightness < 128 else 'light'
    
    # All other colors have dark/normal/light
    if brightness < 85:
        return 'dark'
    elif brightness > 170:
        return 'light'
    else:
        return 'normal'


# =============================================================================
# PURCHASED ARTWORK CLEANUP (files in sold-archive)
# =============================================================================

def cleanup_purchased_artwork() -> Dict[str, Any]:
    """
    Clean up purchased artwork older than 3 days.
    
    User's copy is in users/{user_id}/purchased-art/ (permanent).
    We only delete the sold-thumbnails archive copy after 3 days.
    
    Note: Original and mobile are already deleted during purchase.
    This just cleans orphaned thumbnails if any.
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table('noisemaker-frank-art')
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        
        cutoff_date = datetime.utcnow() - timedelta(days=CLEANUP_DAYS)
        
        # Get purchased artworks older than 3 days
        response = table.scan(
            FilterExpression='is_purchased = :true',
            ExpressionAttributeValues={':true': True}
        )
        
        purchased = response.get('Items', [])
        cleaned = 0
        
        for artwork in purchased:
            artwork_id = artwork.get('artwork_id')
            purchase_date_str = artwork.get('purchase_date')
            already_cleaned = artwork.get('cleaned_up', False)
            
            if already_cleaned:
                continue
                
            if not purchase_date_str:
                continue
            
            try:
                purchase_date = datetime.fromisoformat(purchase_date_str.replace('Z', '+00:00'))
                if purchase_date.replace(tzinfo=None) >= cutoff_date:
                    continue  # Not old enough
            except ValueError:
                continue
            
            # Mark as cleaned in DynamoDB
            table.update_item(
                Key={'artwork_id': artwork_id},
                UpdateExpression='SET cleaned_up = :true, cleanup_date = :date',
                ExpressionAttributeValues={
                    ':true': True,
                    ':date': datetime.utcnow().isoformat()
                }
            )
            
            cleaned += 1
            logger.info(f"Marked cleaned: {artwork_id}")
        
        logger.info(f"Purchased cleanup complete: {cleaned} artworks marked")
        
        return {
            'success': True,
            'cleaned_count': cleaned
        }
        
    except Exception as e:
        logger.error(f"Purchased cleanup failed: {e}")
        return {'success': False, 'error': str(e)}


# =============================================================================
# RECYCLE OLD UNPURCHASED IMAGES (to content-colortemplates)
# =============================================================================

def recycle_oldest_unpurchased(needed_slots: int) -> Dict[str, Any]:
    """
    Recycle oldest never-downloaded images to content-colortemplates.
    Called when pool is full and generator needs to add new images.
    
    Instead of deleting, we:
    1. Analyze the image color
    2. Move original to content-colortemplates/{color}/{shade}/
    3. Delete mobile and thumbnail
    4. Remove from DynamoDB
    
    Args:
        needed_slots: Number of images to recycle
        
    Returns:
        Dict with recycled count and details
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table('noisemaker-frank-art')
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        
        # Get unpurchased, never-downloaded artworks
        response = table.scan(
            FilterExpression='is_purchased = :false AND download_count = :zero',
            ExpressionAttributeValues={':false': False, ':zero': 0}
        )
        
        candidates = response.get('Items', [])
        
        if not candidates:
            logger.info("No candidates for recycling")
            return {'success': True, 'recycled': 0, 'reason': 'No candidates'}
        
        # Sort by upload date (oldest first)
        candidates.sort(key=lambda x: x.get('upload_date', ''))
        
        # Take only what we need
        to_recycle = candidates[:needed_slots]
        recycled = 0
        recycled_details = []
        
        for artwork in to_recycle:
            artwork_id = artwork['artwork_id']
            filename = f"{artwork_id}.png"
            
            try:
                # Download original for color analysis
                original_key = f"{POOL_ORIGINAL}{filename}"
                response = s3_client.get_object(Bucket=S3_BUCKET, Key=original_key)
                image_bytes = response['Body'].read()
                
                # Analyze color
                color, shade = analyze_image_color(image_bytes)
                
                # Destination path
                dest_key = f"{COLOR_TEMPLATES}{color}/{shade}/{filename}"
                
                # Upload to color templates
                s3_client.put_object(
                    Bucket=S3_BUCKET,
                    Key=dest_key,
                    Body=image_bytes,
                    ContentType='image/png'
                )
                logger.info(f"Recycled to: {dest_key}")
                
                # Delete from pool (all 3 sizes)
                for prefix in [POOL_ORIGINAL, POOL_MOBILE, POOL_THUMBNAIL]:
                    try:
                        s3_client.delete_object(Bucket=S3_BUCKET, Key=f"{prefix}{filename}")
                    except Exception:
                        pass
                
                # Remove from DynamoDB
                table.delete_item(Key={'artwork_id': artwork_id})
                
                recycled += 1
                recycled_details.append({
                    'artwork_id': artwork_id,
                    'recycled_to': f"{color}/{shade}"
                })
                
            except Exception as e:
                logger.error(f"Failed to recycle {artwork_id}: {e}")
        
        logger.info(f"Recycled {recycled}/{needed_slots} images to color templates")
        
        return {
            'success': True,
            'recycled': recycled,
            'details': recycled_details
        }
        
    except Exception as e:
        logger.error(f"Recycle failed: {e}")
        return {'success': False, 'error': str(e)}


# =============================================================================
# MAIN WEEKLY JOB
# =============================================================================

def run_weekly_cleanup() -> Dict[str, Any]:
    """
    Main cleanup function - runs weekly via EventBridge (Mondays).
    
    1. Clean purchased artwork older than 3 days
    2. Check if pool needs recycling (handled by generator, not here)
    """
    logger.info("=" * 60)
    logger.info("FRANK'S GARAGE - WEEKLY CLEANUP")
    logger.info("=" * 60)
    
    start_time = datetime.utcnow()
    
    # Clean purchased artwork
    purchased_result = cleanup_purchased_artwork()
    
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    logger.info("=" * 60)
    logger.info(f"CLEANUP COMPLETE - {duration:.1f}s")
    logger.info("=" * 60)
    
    return {
        'success': True,
        'purchased_cleanup': purchased_result,
        'duration_seconds': duration,
        'timestamp': start_time.isoformat()
    }


# =============================================================================
# LAMBDA HANDLER
# =============================================================================

def lambda_handler(event, context):
    """AWS Lambda entry point. Triggered by EventBridge weekly."""
    try:
        return run_weekly_cleanup()
    except Exception as e:
        logger.error(f"Lambda failed: {e}")
        return {'success': False, 'error': str(e)}


# =============================================================================
# LOCAL TESTING
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Frank's Garage Cleanup")
    parser.add_argument('--purchased', action='store_true', help='Clean purchased artwork')
    parser.add_argument('--recycle', type=int, help='Recycle N oldest images')
    parser.add_argument('--full', action='store_true', help='Run full weekly cleanup')
    args = parser.parse_args()
    
    if args.purchased:
        result = cleanup_purchased_artwork()
        print(f"Purchased cleanup: {result}")
    elif args.recycle:
        result = recycle_oldest_unpurchased(args.recycle)
        print(f"Recycled: {result}")
    elif args.full:
        result = run_weekly_cleanup()
        print(f"Weekly cleanup: {result}")
    else:
        print("Use --purchased, --recycle N, or --full")