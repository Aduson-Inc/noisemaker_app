"""
Frank's Garage - Weekly Cleanup Job
=====================================

Runs weekly (Mondays via EventBridge) to clean up purchased artwork files.

For purchased images 2+ days old:
1. Delete original (2000x2000) from sold-archive/
2. Delete mobile (600x600) from sold-archive/
3. Move thumbnail (200x200) to purchased-permanent/

This preserves thumbnails for "My Collection" display while freeing up storage.
"""

import boto3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
S3_BUCKET = 'noisemakerpromobydoowopp'
SOLD_ARCHIVE_PREFIX = 'ArtSellingONLY/sold-archive/'
PERMANENT_PREFIX = 'ArtSellingONLY/purchased-permanent/'
AWS_REGION = 'us-east-2'

# Cleanup threshold (days after purchase)
CLEANUP_DAYS = 2


def get_purchased_artworks_for_cleanup() -> List[Dict[str, Any]]:
    """
    Get list of purchased artworks that are 2+ days old and need cleanup.

    Returns:
        List of artwork records needing cleanup
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table('noisemaker-frank-art')

        # Get all purchased artworks
        response = table.scan(
            FilterExpression='is_purchased = :true',
            ExpressionAttributeValues={':true': True}
        )

        purchased = response.get('Items', [])

        # Filter to those 2+ days old
        cutoff_date = datetime.utcnow() - timedelta(days=CLEANUP_DAYS)

        artworks_to_cleanup = []
        for artwork in purchased:
            purchase_date_str = artwork.get('purchase_date') or artwork.get('purchased_at')
            if purchase_date_str:
                try:
                    purchase_date = datetime.fromisoformat(purchase_date_str.replace('Z', '+00:00'))
                    if purchase_date.replace(tzinfo=None) < cutoff_date:
                        # Check if already cleaned up
                        if not artwork.get('cleaned_up', False):
                            artworks_to_cleanup.append(artwork)
                except ValueError:
                    logger.warning(f"Invalid purchase date for {artwork.get('artwork_id')}")

        logger.info(f"Found {len(artworks_to_cleanup)} artworks needing cleanup")
        return artworks_to_cleanup

    except Exception as e:
        logger.error(f"Error getting purchased artworks: {e}")
        return []


def cleanup_artwork(artwork: Dict[str, Any]) -> bool:
    """
    Clean up a single purchased artwork.

    1. Delete original and mobile from sold-archive/
    2. Move thumbnail to purchased-permanent/
    3. Mark as cleaned up in DynamoDB

    Args:
        artwork: Artwork record from DynamoDB

    Returns:
        True if cleanup successful
    """
    try:
        artwork_id = artwork['artwork_id']
        filename = artwork.get('filename', f"{artwork_id}.png")

        s3_client = boto3.client('s3', region_name=AWS_REGION)
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table('noisemaker-frank-art')

        logger.info(f"Cleaning up artwork: {artwork_id}")

        # 1. Delete original (2000x2000) from sold-archive
        original_key = f"{SOLD_ARCHIVE_PREFIX}original/{filename}"
        try:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=original_key)
            logger.info(f"  ✓ Deleted original: {original_key}")
        except Exception as e:
            logger.warning(f"  ! Could not delete original: {e}")

        # 2. Delete mobile (600x600) from sold-archive
        mobile_key = f"{SOLD_ARCHIVE_PREFIX}mobile/{filename}"
        try:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=mobile_key)
            logger.info(f"  ✓ Deleted mobile: {mobile_key}")
        except Exception as e:
            logger.warning(f"  ! Could not delete mobile: {e}")

        # 3. Move thumbnail to purchased-permanent
        thumbnail_source = f"{SOLD_ARCHIVE_PREFIX}thumbnails/{filename}"
        thumbnail_dest = f"{PERMANENT_PREFIX}{filename}"

        try:
            # Copy to permanent location
            s3_client.copy_object(
                Bucket=S3_BUCKET,
                CopySource={'Bucket': S3_BUCKET, 'Key': thumbnail_source},
                Key=thumbnail_dest
            )
            # Delete from sold-archive
            s3_client.delete_object(Bucket=S3_BUCKET, Key=thumbnail_source)
            logger.info(f"  ✓ Moved thumbnail to permanent: {thumbnail_dest}")
        except Exception as e:
            logger.warning(f"  ! Could not move thumbnail: {e}")

        # 4. Mark as cleaned up in DynamoDB
        table.update_item(
            Key={'artwork_id': artwork_id},
            UpdateExpression='SET cleaned_up = :true, cleanup_date = :date',
            ExpressionAttributeValues={
                ':true': True,
                ':date': datetime.utcnow().isoformat()
            }
        )

        logger.info(f"  ✓ Marked as cleaned up in DynamoDB")
        return True

    except Exception as e:
        logger.error(f"Error cleaning up artwork {artwork.get('artwork_id')}: {e}")
        return False


def run_weekly_cleanup() -> Dict[str, Any]:
    """
    Main cleanup function - run weekly via EventBridge.

    Returns:
        Cleanup results summary
    """
    logger.info("=" * 80)
    logger.info("🧹 STARTING WEEKLY CLEANUP - Frank's Garage")
    logger.info("=" * 80)

    start_time = datetime.utcnow()

    # Get artworks needing cleanup
    artworks = get_purchased_artworks_for_cleanup()

    if not artworks:
        logger.info("No artworks need cleanup at this time")
        return {
            'success': True,
            'artworks_cleaned': 0,
            'message': 'No cleanup needed'
        }

    # Clean up each artwork
    cleaned_count = 0
    failed_count = 0

    for artwork in artworks:
        if cleanup_artwork(artwork):
            cleaned_count += 1
        else:
            failed_count += 1

    # Calculate storage saved (estimated)
    # Original: ~2MB, Mobile: ~500KB = ~2.5MB per artwork
    storage_saved_mb = cleaned_count * 2.5

    duration = (datetime.utcnow() - start_time).total_seconds()

    logger.info("=" * 80)
    logger.info("🧹 CLEANUP COMPLETE")
    logger.info("=" * 80)
    logger.info(f"  ✅ Cleaned: {cleaned_count}")
    logger.info(f"  ❌ Failed: {failed_count}")
    logger.info(f"  💾 Storage saved: ~{storage_saved_mb:.1f} MB")
    logger.info(f"  ⏱️ Duration: {duration:.1f}s")

    return {
        'success': True,
        'artworks_cleaned': cleaned_count,
        'artworks_failed': failed_count,
        'storage_saved_mb': storage_saved_mb,
        'duration_seconds': duration,
        'timestamp': start_time.isoformat()
    }


def cleanup_oldest_unpurchased(needed_slots: int) -> int:
    """
    Remove oldest never-downloaded images to make room in pool.
    Only removes what's needed (e.g., pool=248, adding 4, remove 2).

    Args:
        needed_slots: Number of slots to free up

    Returns:
        Number of artworks removed
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table('noisemaker-frank-art')
        s3_client = boto3.client('s3', region_name=AWS_REGION)

        # Get all unpurchased, never-downloaded artworks
        response = table.scan(
            FilterExpression='is_purchased = :false AND download_count = :zero',
            ExpressionAttributeValues={
                ':false': False,
                ':zero': 0
            }
        )

        candidates = response.get('Items', [])

        if not candidates:
            logger.info("No never-downloaded artworks to remove")
            return 0

        # Sort by upload date (oldest first)
        candidates.sort(key=lambda x: x.get('upload_date', ''))

        # Remove only what's needed
        to_remove = candidates[:needed_slots]
        removed_count = 0

        for artwork in to_remove:
            artwork_id = artwork['artwork_id']
            filename = artwork.get('filename', f"{artwork_id}.png")

            try:
                # Delete from S3 (all 3 sizes)
                for folder in ['original', 'mobile', 'thumbnails']:
                    key = f"ArtSellingONLY/{folder}/{filename}"
                    s3_client.delete_object(Bucket=S3_BUCKET, Key=key)

                # Delete from DynamoDB
                table.delete_item(Key={'artwork_id': artwork_id})

                removed_count += 1
                logger.info(f"Removed oldest artwork: {artwork_id}")

            except Exception as e:
                logger.error(f"Error removing artwork {artwork_id}: {e}")

        return removed_count

    except Exception as e:
        logger.error(f"Error in cleanup_oldest_unpurchased: {e}")
        return 0


# AWS Lambda handler
def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    Triggered by EventBridge weekly (Mondays at midnight UTC).
    """
    try:
        return run_weekly_cleanup()
    except Exception as e:
        logger.error(f"Fatal error in cleanup lambda: {e}")
        return {
            'success': False,
            'error': str(e)
        }


# Local testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Frank's Garage Weekly Cleanup")
    parser.add_argument('--dry-run', action='store_true', help='Show what would be cleaned without deleting')
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN MODE - No files will be deleted")
        artworks = get_purchased_artworks_for_cleanup()
        for art in artworks:
            print(f"  Would cleanup: {art.get('artwork_id')} (purchased: {art.get('purchase_date')})")
    else:
        result = run_weekly_cleanup()
        print(f"\nResult: {result}")
