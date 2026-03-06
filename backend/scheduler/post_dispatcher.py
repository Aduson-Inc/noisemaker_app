"""
NOiSEMaKER Post Dispatcher
============================

Lambda entry point. Runs hourly via EventBridge across all 24 UTC hours.
Queries noisemaker-scheduled-posts for pending posts due within the current hour,
dispatches them to social media platforms, and records results.

Flow per post:
1. Load content (image/video + caption) from noisemaker-content
2. Determine media_type (image or video) from content record
3. Download media from S3
4. Post to platform via multi_platform_poster
5. Update post status, content posted_to counts, and posting history
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta

import boto3
from boto3.dynamodb.conditions import Key

from content.multi_platform_poster import (
    MultiPlatformPostingEngine,
    PostContent,
    PostResult,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# =============================================================================
# CONFIGURATION
# =============================================================================

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
S3_BUCKET = os.environ.get("S3_BUCKET", "noisemakerpromobydoowopp")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

scheduled_table = dynamodb.Table("noisemaker-scheduled-posts")
content_table = dynamodb.Table("noisemaker-content")
history_table = dynamodb.Table("noisemaker-posting-history")

MAX_RETRIES = 2

posting_engine = MultiPlatformPostingEngine()


# =============================================================================
# QUERY
# =============================================================================

def _get_due_posts() -> list[dict]:
    """
    Query the status-scheduled_time-index GSI for pending posts
    with scheduled_time between now and now + 1 hour.
    """
    now = datetime.now(timezone.utc)
    one_hour_later = now + timedelta(hours=1)

    now_iso = now.isoformat()
    later_iso = one_hour_later.isoformat()

    posts = []
    query_kwargs = {
        "IndexName": "status-scheduled_time-index",
        "KeyConditionExpression": (
            Key("status").eq("pending")
            & Key("scheduled_time").between(now_iso, later_iso)
        ),
    }

    while True:
        response = scheduled_table.query(**query_kwargs)
        posts.extend(response.get("Items", []))

        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        query_kwargs["ExclusiveStartKey"] = last_key

    logger.info(f"Found {len(posts)} pending posts due in the next hour")
    return posts


# =============================================================================
# DATA LOADING
# =============================================================================

def _load_content(user_id: str, content_id: str) -> dict | None:
    """Load content record from noisemaker-content."""
    try:
        response = content_table.get_item(
            Key={"user_id": user_id, "content_id": content_id}
        )
        return response.get("Item")
    except Exception as e:
        logger.error(f"Failed to load content {content_id}: {e}")
        return None


def _download_media_from_s3(s3_key: str) -> str | None:
    """
    Download media (image or video) from S3 to a temporary file path.
    Returns the local file path, or None on failure.
    """
    if not s3_key:
        logger.error("Empty S3 key provided")
        return None
    try:
        local_path = f"/tmp/{s3_key.replace('/', '_')}"
        s3_client.download_file(S3_BUCKET, s3_key, local_path)
        logger.info(f"Downloaded media: {s3_key}")
        return local_path
    except Exception as e:
        logger.error(f"S3 download failed for {s3_key}: {e}")
        return None


# =============================================================================
# STATUS UPDATES
# =============================================================================

def _mark_posted(post: dict) -> None:
    """Update scheduled post status to 'posted'."""
    scheduled_table.update_item(
        Key={"user_id": post["user_id"], "post_id": post["post_id"]},
        UpdateExpression="SET #s = :s, posted_at = :t",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":s": "posted",
            ":t": datetime.now(timezone.utc).isoformat(),
        },
    )


def _mark_failed(post: dict, error_message: str) -> None:
    """Update scheduled post status to 'failed' with error details."""
    scheduled_table.update_item(
        Key={"user_id": post["user_id"], "post_id": post["post_id"]},
        UpdateExpression="SET #s = :s, error_message = :e",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":s": "failed",
            ":e": error_message,
        },
    )


def _requeue_post(post: dict) -> None:
    """
    Re-queue a failed post with the next available hour.
    Increments retry_count. Gives up after MAX_RETRIES.
    """
    retry_count = int(post.get("retry_count", 0)) + 1

    if retry_count > MAX_RETRIES:
        logger.warning(
            f"Post {post['post_id']} exceeded max retries ({MAX_RETRIES}), "
            "marking as failed"
        )
        _mark_failed(post, f"Exceeded max retries ({MAX_RETRIES})")
        return

    # Schedule for the next hour
    next_time = datetime.now(timezone.utc) + timedelta(hours=1)

    scheduled_table.update_item(
        Key={"user_id": post["user_id"], "post_id": post["post_id"]},
        UpdateExpression=(
            "SET #s = :s, scheduled_time = :t, retry_count = :r"
        ),
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":s": "pending",
            ":t": next_time.isoformat(),
            ":r": retry_count,
        },
    )
    logger.info(
        f"Re-queued post {post['post_id']} for {next_time.isoformat()} "
        f"(retry {retry_count}/{MAX_RETRIES})"
    )


def _update_content_posted_to(
    user_id: str, content_id: str, platform: str
) -> None:
    """Increment the posted_to count for this platform on the content record."""
    try:
        content_table.update_item(
            Key={"user_id": user_id, "content_id": content_id},
            UpdateExpression="SET posted_to.#p = if_not_exists(posted_to.#p, :zero) + :one",
            ExpressionAttributeNames={"#p": platform},
            ExpressionAttributeValues={
                ":zero": 0,
                ":one": 1,
            },
        )
    except Exception as e:
        logger.error(f"Failed to update posted_to for content {content_id}: {e}")


def _check_content_exhausted(user_id: str, content_id: str) -> None:
    """
    Check if content has hit max posts on all platforms.
    If so, mark status = 'exhausted'.

    Reads song_count from the content record to determine the threshold:
        - song_count == 3: max 1 post per platform
        - song_count 1 or 2: max 2 posts per platform

    FOLLOW-UP REQUIRED: content_generator.py must be updated to store
    song_count on the content record at generation time. Until then,
    content records missing song_count will default to threshold 1.
    """
    try:
        content = _load_content(user_id, content_id)
        if not content or content.get("status") != "active":
            return

        posted_to = content.get("posted_to", {})
        if not posted_to:
            return

        # Read song_count from content record to determine threshold
        song_count = int(content.get("song_count", 3))
        max_per_platform = 1 if song_count == 3 else 2

        all_at_max = all(
            int(v) >= max_per_platform for v in posted_to.values()
        )

        if all_at_max:
            content_table.update_item(
                Key={"user_id": user_id, "content_id": content_id},
                UpdateExpression="SET #s = :s",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={":s": "exhausted"},
            )
            logger.info(f"Content {content_id} marked as exhausted")

    except Exception as e:
        logger.error(f"Exhaustion check failed for content {content_id}: {e}")


# =============================================================================
# HISTORY
# =============================================================================

def _write_history(
    post: dict, platform_post_id: str | None, status: str,
    error_message: str | None
) -> None:
    """Write a record to noisemaker-posting-history."""
    try:
        history_table.put_item(Item={
            "user_id": post["user_id"],
            "post_id": post["post_id"],
            "content_id": post.get("content_id", ""),
            "song_id": post.get("song_id", ""),
            "platform": post.get("platform", ""),
            "posted_at": datetime.now(timezone.utc).isoformat(),
            "platform_post_id": platform_post_id or "",
            "status": status,
            "error_message": error_message or "",
        })
    except Exception as e:
        logger.error(f"Failed to write posting history for {post['post_id']}: {e}")


# =============================================================================
# DISPATCH
# =============================================================================

def _dispatch_post(post: dict) -> bool:
    """
    Dispatch a single scheduled post to its target platform.
    Returns True on success, False on failure.
    """
    user_id = post["user_id"]
    content_id = post.get("content_id", "")
    platform = post.get("platform", "")

    # Load content
    content = _load_content(user_id, content_id)
    if not content:
        error = f"Content {content_id} not found"
        _mark_failed(post, error)
        _write_history(post, None, "failed", error)
        return False

    # Determine media type and download from S3
    media_type = content.get("media_type", "image")
    if media_type == "video":
        media_s3_key = content.get("video_s3_key", "")
    else:
        media_s3_key = content.get("image_s3_key", "")

    media_path = _download_media_from_s3(media_s3_key)
    if not media_path:
        error = f"Media download failed: {media_s3_key}"
        _mark_failed(post, error)
        _requeue_post(post)
        _write_history(post, None, "failed", error)
        return False

    # Build PostContent for multi_platform_poster
    post_content = PostContent(
        caption=content.get("caption", ""),
        image_path=media_path if media_type == "image" else "",
        hashtags=[],
        streaming_links={},
        platform=platform,
        video_path=media_path if media_type == "video" else None,
        media_type=media_type,
    )

    # Post via the posting engine
    try:
        results = posting_engine.post_to_platforms(user_id, post_content, [platform])
        result = results.get(platform)
    except Exception as e:
        logger.error(f"Posting engine error for {post['post_id']}: {e}")
        result = PostResult(
            success=False,
            platform=platform,
            error_message=str(e),
        )

    if result and result.success:
        _mark_posted(post)
        _update_content_posted_to(user_id, content_id, platform)
        _check_content_exhausted(user_id, content_id)
        _write_history(post, result.post_id, "posted", None)
        logger.info(f"Posted {post['post_id']} to {platform}")
        return True
    else:
        error = result.error_message if result else "Unknown posting error"
        _mark_failed(post, error)
        _requeue_post(post)
        _write_history(post, None, "failed", error)
        logger.warning(f"Failed to post {post['post_id']} to {platform}: {error}")
        return False


# =============================================================================
# LAMBDA HANDLER
# =============================================================================

def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    Triggered hourly by EventBridge.
    Dispatches all pending posts due within the current hour.
    """
    logger.info("=" * 60)
    logger.info("POST DISPATCHER - Starting")
    logger.info("=" * 60)

    try:
        posts = _get_due_posts()

        succeeded = 0
        failed = 0

        for post in posts:
            try:
                if _dispatch_post(post):
                    succeeded += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Unhandled error dispatching {post.get('post_id')}: {e}")
                failed += 1

        summary = {
            "posts_attempted": len(posts),
            "posts_succeeded": succeeded,
            "posts_failed": failed,
        }

        logger.info(
            f"COMPLETE: {succeeded} succeeded, {failed} failed "
            f"out of {len(posts)} posts"
        )
        logger.info("=" * 60)

        return {
            "statusCode": 200,
            "body": json.dumps(summary),
        }

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"success": False, "error": str(e)}),
        }
