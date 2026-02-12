"""
NOiSEMaKER Daily Orchestrator
==============================

Lambda entry point. Runs every 30 minutes via EventBridge.
For each paying user, checks if it's currently 9 PM in THEIR timezone.
If yes, processes that user's daily posting schedule. If no, skips.

Flow per user:
1. Determine tomorrow's (song, platform) pairs via schedule_engine
2. Check for reusable content or generate new content
3. Pick optimal posting times and schedule posts
4. Advance schedule_day and days_in_promotion counters
5. Handle extended promo songs on a separate 3-day rotation
"""

import os
import uuid
import json
import logging
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

import boto3
from boto3.dynamodb.conditions import Key, Attr

from scheduler.schedule_engine import get_tomorrows_posts, increment_schedule_day
from content.content_generator import (
    generate_content,
    check_content_available,
    extract_and_cache_colors,
)
from scheduler.posting_schedule import select_random_posting_time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# =============================================================================
# CONFIGURATION
# =============================================================================

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
users_table = dynamodb.Table("noisemaker-users")
songs_table = dynamodb.Table("noisemaker-songs")
platforms_table = dynamodb.Table("noisemaker-platform-connections")
scheduled_table = dynamodb.Table("noisemaker-scheduled-posts")

TRIGGER_HOUR = 21  # 9 PM local time
MAX_PROMO_DAYS = 42
EXTENDED_POST_INTERVAL_DAYS = 3


# =============================================================================
# USER DISCOVERY
# =============================================================================

def _get_paying_users() -> list[dict]:
    """Scan noisemaker-users for all users with a non-empty subscription_tier."""
    users = []
    scan_kwargs = {
        "FilterExpression": (
            Attr("subscription_tier").exists()
            & Attr("subscription_tier").ne("")
        ),
    }

    while True:
        response = users_table.scan(**scan_kwargs)
        users.extend(response.get("Items", []))

        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        scan_kwargs["ExclusiveStartKey"] = last_key

    logger.info(f"Found {len(users)} paying users")
    return users


def _is_trigger_hour(user: dict) -> bool:
    """Return True if it's currently 9 PM in the user's timezone."""
    user_tz = _resolve_user_tz(user)
    local_now = datetime.now(timezone.utc).astimezone(user_tz)
    return local_now.hour == TRIGGER_HOUR


# =============================================================================
# DATA LOADING
# =============================================================================

def _get_active_songs(user_id: str) -> list[dict]:
    """Get songs with days_in_promotion <= 42, not retired, not extended."""
    response = songs_table.query(
        KeyConditionExpression=Key("user_id").eq(user_id),
        FilterExpression=(
            Attr("days_in_promotion").lte(MAX_PROMO_DAYS)
            & Attr("promotion_status").ne("retired")
            & Attr("promotion_status").ne("extended")
        ),
    )
    return response.get("Items", [])


def _get_extended_songs(user_id: str) -> list[dict]:
    """Get songs with promotion_status = 'extended'."""
    response = songs_table.query(
        KeyConditionExpression=Key("user_id").eq(user_id),
        FilterExpression=Attr("promotion_status").eq("extended"),
    )
    return response.get("Items", [])


def _get_connected_platforms(user_id: str) -> list[str]:
    """Get list of actively connected platform names for user."""
    response = platforms_table.query(
        KeyConditionExpression=Key("user_id").eq(user_id),
        FilterExpression=Attr("status").eq("active"),
    )
    items = response.get("Items", [])
    return [item["platform"] for item in items if "platform" in item]


# =============================================================================
# SCHEDULING HELPERS
# =============================================================================

def _resolve_user_tz(user: dict) -> ZoneInfo:
    """Resolve user's timezone, defaulting to America/New_York."""
    tz_name = user.get("timezone", "America/New_York")
    try:
        return ZoneInfo(tz_name)
    except Exception:
        logger.warning(
            f"Invalid timezone '{tz_name}' for user {user.get('user_id')}, "
            "defaulting to America/New_York"
        )
        return ZoneInfo("America/New_York")


def _get_user_tomorrow(user_tz: ZoneInfo) -> datetime:
    """Get tomorrow's date in the user's local timezone."""
    local_now = datetime.now(timezone.utc).astimezone(user_tz)
    return local_now + timedelta(days=1)


def _local_time_to_utc(time_str: str, date: datetime, tz: ZoneInfo) -> str:
    """
    Convert a local HH:MM time string on the given date to a UTC ISO string.
    The date should be tomorrow in the user's local timezone.
    """
    hour, minute = map(int, time_str.split(":"))
    local_dt = datetime(date.year, date.month, date.day, hour, minute, tzinfo=tz)
    utc_dt = local_dt.astimezone(timezone.utc)
    return utc_dt.isoformat()


# =============================================================================
# CORE PROCESSING
# =============================================================================

def _ensure_color_palette(song: dict, user_id: str) -> dict | None:
    """
    If song is missing color_palette or cached_artwork_s3_key,
    extract colors from art_url and reload the song record.
    Returns updated song dict, or None on failure.
    """
    if song.get("color_palette") and song.get("cached_artwork_s3_key"):
        return song

    art_url = song.get("art_url", "")
    if not art_url:
        logger.warning(f"Song {song['song_id']} has no art_url, cannot extract colors")
        return None

    try:
        extract_and_cache_colors(song["song_id"], user_id, art_url)
        refreshed = songs_table.get_item(
            Key={"user_id": user_id, "song_id": song["song_id"]}
        )
        return refreshed.get("Item", song)
    except Exception as e:
        logger.error(f"Color extraction failed for {song['song_id']}: {e}")
        return None


def _build_song_data(song: dict) -> dict:
    """Build the song_data dict expected by generate_content()."""
    return {
        "song_id": song["song_id"],
        "song_name": song.get("song_name", ""),
        "artist_name": song.get("artist_name", ""),
        "genre": song.get("genre", "Music"),
        "color_palette": song.get("color_palette", []),
        "cached_artwork_s3_key": song.get("cached_artwork_s3_key", ""),
    }


def _process_user(user: dict) -> dict:
    """
    Process a single user's daily schedule.
    Returns a summary dict.
    """
    user_id = user["user_id"]
    user_tz = _resolve_user_tz(user)
    tomorrow = _get_user_tomorrow(user_tz)

    logger.info(f"Processing user {user_id}")

    # Load data
    active_songs = _get_active_songs(user_id)
    connected_platforms = _get_connected_platforms(user_id)
    schedule_day = int(user.get("schedule_day", 1))
    song_count = len(active_songs)

    if song_count == 0:
        logger.info(f"User {user_id}: no active songs, skipping")
        return {"user_id": user_id, "status": "skipped", "reason": "no_active_songs"}

    if not connected_platforms:
        logger.info(f"User {user_id}: no connected platforms, skipping")
        return {"user_id": user_id, "status": "skipped", "reason": "no_platforms"}

    # Build user_data for schedule engine
    user_data = {
        "active_songs": [
            {
                "song_id": s["song_id"],
                "days_in_promotion": int(s.get("days_in_promotion", 1)),
            }
            for s in active_songs
        ],
        "connected_platforms": connected_platforms,
        "schedule_day": schedule_day,
    }

    # Get tomorrow's post assignments
    post_pairs = get_tomorrows_posts(user_data)
    logger.info(f"User {user_id}: {len(post_pairs)} posts for schedule_day {schedule_day}")

    # Build song lookup
    song_lookup = {s["song_id"]: s for s in active_songs}
    posts_scheduled = 0

    for pair in post_pairs:
        song_id = pair["song_id"]
        platform = pair["platform"]
        song = song_lookup.get(song_id)

        if not song:
            logger.warning(f"Song {song_id} not in lookup, skipping")
            continue

        # Check for reusable content
        content = check_content_available(user_id, song_id, platform, song_count)

        if content:
            content_id = content["content_id"]
            logger.info(f"Reusing content {content_id} for {song_id}/{platform}")
        else:
            # Ensure color palette exists
            song = _ensure_color_palette(song, user_id)
            if not song:
                continue
            song_lookup[song_id] = song

            # Generate new content
            result = generate_content(_build_song_data(song), platform, user_id)
            if not result:
                logger.error(f"Content generation failed for {song_id}/{platform}")
                continue

            content_id = result["content_id"]
            logger.info(f"Generated content {content_id} for {song_id}/{platform}")

        # Pick posting time and convert to UTC
        local_time_str = select_random_posting_time(platform)
        scheduled_time_utc = _local_time_to_utc(local_time_str, tomorrow, user_tz)

        # Create scheduled post record
        post_id = str(uuid.uuid4())
        scheduled_table.put_item(Item={
            "user_id": user_id,
            "post_id": post_id,
            "content_id": content_id,
            "song_id": song_id,
            "platform": platform,
            "scheduled_time": scheduled_time_utc,
            "status": "pending",
            "schedule_day": schedule_day,
            "schedule_position": pair.get("position", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        posts_scheduled += 1

    # Handle extended promo songs
    extended_scheduled = _process_extended_songs(
        user_id, user_tz, tomorrow, connected_platforms
    )

    # Advance user's schedule_day (1-14 cycle)
    new_day = increment_schedule_day(schedule_day)
    users_table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="SET schedule_day = :d",
        ExpressionAttributeValues={":d": new_day},
    )

    # Increment days_in_promotion for each active song; retire at 43
    for song in active_songs:
        sid = song["song_id"]
        current_days = int(song.get("days_in_promotion", 1))
        new_days = current_days + 1

        if new_days > MAX_PROMO_DAYS:
            songs_table.update_item(
                Key={"user_id": user_id, "song_id": sid},
                UpdateExpression="SET days_in_promotion = :d, promotion_status = :s",
                ExpressionAttributeValues={":d": new_days, ":s": "retired"},
            )
            logger.info(f"Song {sid} retired at day {new_days}")
        else:
            songs_table.update_item(
                Key={"user_id": user_id, "song_id": sid},
                UpdateExpression="SET days_in_promotion = :d",
                ExpressionAttributeValues={":d": new_days},
            )

    return {
        "user_id": user_id,
        "status": "processed",
        "posts_scheduled": posts_scheduled,
        "extended_scheduled": extended_scheduled,
        "schedule_day": f"{schedule_day} -> {new_day}",
        "active_songs": song_count,
    }


# =============================================================================
# EXTENDED PROMO HANDLING
# =============================================================================

def _process_extended_songs(
    user_id: str, user_tz: ZoneInfo, tomorrow: datetime, platforms: list[str]
) -> int:
    """
    Handle extended promo songs ($10/month).
    Posts every 3 days, rotating through connected platforms.
    Does NOT use schedule grids or A/B/C system.

    Tracks last_extended_post_date and last_extended_platform_index on song record.
    Returns number of extended posts scheduled.
    """
    extended_songs = _get_extended_songs(user_id)
    if not extended_songs or not platforms:
        return 0

    scheduled = 0
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for song in extended_songs:
        last_post_date = song.get("last_extended_post_date", "")
        platform_idx = int(song.get("last_extended_platform_index", -1))

        # Check if 3+ days since last post
        if last_post_date:
            try:
                last_dt = datetime.strptime(last_post_date, "%Y-%m-%d")
                days_since = (datetime.strptime(today_str, "%Y-%m-%d") - last_dt).days
                if days_since < EXTENDED_POST_INTERVAL_DAYS:
                    continue
            except ValueError:
                pass  # Invalid date — proceed with posting

        # Rotate to next platform
        next_idx = (platform_idx + 1) % len(platforms)
        platform = platforms[next_idx]
        song_id = song["song_id"]

        # Ensure color palette exists
        song = _ensure_color_palette(song, user_id)
        if not song:
            continue

        # Generate new content (always new for extended — no reuse)
        result = generate_content(_build_song_data(song), platform, user_id)
        if not result:
            logger.error(f"Extended content gen failed for {song_id}/{platform}")
            continue

        # Schedule post
        local_time_str = select_random_posting_time(platform)
        scheduled_time_utc = _local_time_to_utc(local_time_str, tomorrow, user_tz)

        post_id = str(uuid.uuid4())
        scheduled_table.put_item(Item={
            "user_id": user_id,
            "post_id": post_id,
            "content_id": result["content_id"],
            "song_id": song_id,
            "platform": platform,
            "scheduled_time": scheduled_time_utc,
            "status": "pending",
            "schedule_day": 0,
            "schedule_position": "extended",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

        # Update song's extended tracking fields
        songs_table.update_item(
            Key={"user_id": user_id, "song_id": song_id},
            UpdateExpression=(
                "SET last_extended_post_date = :d, "
                "last_extended_platform_index = :i"
            ),
            ExpressionAttributeValues={
                ":d": today_str,
                ":i": next_idx,
            },
        )

        scheduled += 1
        logger.info(f"Extended post scheduled: {song_id} -> {platform}")

    return scheduled


# =============================================================================
# LAMBDA HANDLER
# =============================================================================

def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    Triggered every 30 minutes by EventBridge.
    Processes users whose local time is currently 9 PM.
    """
    logger.info("=" * 60)
    logger.info("DAILY ORCHESTRATOR - Starting")
    logger.info("=" * 60)

    try:
        users = _get_paying_users()
        results = []

        for user in users:
            user_id = user["user_id"]

            if not _is_trigger_hour(user):
                continue

            try:
                result = _process_user(user)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing user {user_id}: {e}")
                results.append({
                    "user_id": user_id,
                    "status": "error",
                    "error": str(e),
                })

        processed = [r for r in results if r.get("status") == "processed"]
        errored = [r for r in results if r.get("status") == "error"]

        summary = {
            "users_scanned": len(users),
            "users_triggered": len(results),
            "users_processed": len(processed),
            "users_errored": len(errored),
            "results": results,
        }

        logger.info(
            f"COMPLETE: {len(processed)} processed, {len(errored)} errors "
            f"out of {len(users)} paying users"
        )
        logger.info("=" * 60)

        return {
            "statusCode": 200,
            "body": json.dumps(summary, default=str),
        }

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"success": False, "error": str(e)}),
        }
