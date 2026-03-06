"""
NOiSEMaKER Content Generator
=============================

Generates platform-specific promotional content (images AND videos) for user songs.

Pipeline:
1. Analyze artwork via vision model (or PIL fallback) for mood/color data
2. Generate AI background enriched with mood analysis via model_router
3. Select template and render (static PIL for images, FFmpeg for videos)
4. Build caption context from RAG pipeline (song metadata enrichment)
5. Generate caption via Grok AI (or template fallback)
6. Upload to S3 and record in DynamoDB

Supported platforms: instagram, twitter, facebook, threads, reddit, discord (images)
                     tiktok, youtube (videos, with static image fallback)

Content reuse rules:
    - 1 or 2-song mode: content can be posted TWICE to same platform before regeneration
    - 3-song mode: content can be posted ONCE per platform before regeneration
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from io import BytesIO
from typing import Optional

import boto3
import requests
from boto3.dynamodb.conditions import Key, Attr
from PIL import Image
from content.caption_generator import generate_caption
from content.asset_pipeline import analyze_artwork, generate_background, download_artwork_from_s3
from content.template_engine import select_template, render_static, render_video
from content.rag_pipeline import build_caption_context

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
S3_BUCKET = os.environ.get("S3_BUCKET", "noisemakerpromobydoowopp")

# Platform dimensions and media type
# "image" platforms get static JPEG composites
# "video" platforms get FFmpeg-rendered MP4s (with optional audio)
PLATFORM_SIZES = {
    "instagram": (1080, 1080),
    "twitter": (1200, 675),
    "facebook": (1200, 630),
    "threads": (1080, 1080),
    "reddit": (1200, 630),
    "discord": (1200, 675),
    "tiktok": (1080, 1920),
    "youtube": (1080, 1920),
}

VIDEO_PLATFORMS = {"tiktok", "youtube"}

# =============================================================================
# AWS CLIENTS
# =============================================================================

s3_client = boto3.client("s3", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)


# =============================================================================
# PUBLIC API
# =============================================================================

def generate_content(song_data: dict, platform: str, user_id: str, song_count: int = 3) -> dict:
    """
    Generate promotional content (image or video) for a song on a specific platform.

    Pipeline:
        1. Analyze artwork (vision model or PIL fallback) → mood + color data
        2. Generate AI background enriched with mood analysis
        3. Select template and render (static PIL for image, FFmpeg for video)
        4. Build caption context from RAG pipeline
        5. Generate caption (Grok AI or template fallback)
        6. Upload to S3 and record in DynamoDB

    Args:
        song_data: dict with song_id, song_name, artist_name, genre,
                   color_palette (list of 3 hex strings), cached_artwork_s3_key
        platform: target platform name
        user_id: the user's ID
        song_count: number of active songs (affects content reuse rules)

    Returns:
        dict with content_id, image_s3_key or video_s3_key, caption, media_type.
        Empty dict if generation fails.
    """
    size = PLATFORM_SIZES.get(platform)
    if size is None:
        logger.warning(f"Unknown platform: {platform}")
        return {}

    is_video = platform in VIDEO_PLATFORMS
    content_id = str(uuid.uuid4())
    uid_int = uuid.UUID(content_id).int

    # Step 1: Analyze artwork for mood and color
    mood_analysis = analyze_artwork(song_data)

    # Step 2: Generate AI background
    background = generate_background(mood_analysis, platform, size, uid_int)
    if background is None:
        logger.error(f"Background generation failed for {platform}")
        return {}

    # Step 3: Download cached artwork from S3
    artwork = download_artwork_from_s3(song_data.get("cached_artwork_s3_key", ""))
    if artwork is None:
        logger.error("Artwork download failed")
        return {}

    # Step 4: Select template and render
    template = select_template(platform, size)
    render_assets = {
        "background": background,
        "artwork": artwork,
        "song_title": song_data.get("song_name", ""),
        "artist_name": song_data.get("artist_name", ""),
    }

    if is_video:
        audio_key = song_data.get("audio_clip_s3_key")
        rendered_bytes = render_video(template, render_assets, audio_key)
        if rendered_bytes is None:
            # FFmpeg unavailable or failed — fall back to static image
            logger.warning(f"Video render failed for {platform}, falling back to static")
            rendered_bytes = render_static(template, render_assets)
            is_video = False
    else:
        rendered_bytes = render_static(template, render_assets)

    if rendered_bytes is None:
        logger.error("Render failed — no output bytes")
        return {}

    # Step 5: Build caption context and generate caption
    caption_context = build_caption_context(user_id, song_data)
    caption = generate_caption(
        song_data.get("song_name", ""),
        song_data.get("artist_name", ""),
        song_data.get("genre", "Music"),
        platform,
        context=caption_context,
    )

    # Step 6: Upload to S3
    media_type = "video" if is_video else "image"
    ext = "mp4" if is_video else "jpg"
    content_type = "video/mp4" if is_video else "image/jpeg"
    s3_key = f"content/{user_id}/{content_id}.{ext}"

    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=rendered_bytes,
            ContentType=content_type,
        )
        logger.info(f"Uploaded {media_type}: s3://{S3_BUCKET}/{s3_key}")
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")
        return {}

    # Step 7: Store record in DynamoDB
    media_key_field = "video_s3_key" if is_video else "image_s3_key"
    table = dynamodb.Table("noisemaker-content")
    try:
        table.put_item(Item={
            "user_id": user_id,
            "content_id": content_id,
            "song_id": song_data["song_id"],
            media_key_field: s3_key,
            "platform": platform,
            "caption": caption,
            "caption_context": caption_context,
            "media_type": media_type,
            "color_palette": song_data.get("color_palette", []),
            "song_count": song_count,
            "posted_to": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
        })
        logger.info(f"Content record stored: {content_id} ({media_type})")
    except Exception as e:
        logger.error(f"DynamoDB write failed: {e}")
        return {}

    return {
        "content_id": content_id,
        media_key_field: s3_key,
        "caption": caption,
        "media_type": media_type,
    }



def extract_and_cache_colors(song_id: str, user_id: str, art_url: str) -> list:
    """
    Download artwork from Spotify, extract 3 dominant hex colors, cache to S3.
    Updates the song record in noisemaker-songs with color_palette and
    cached_artwork_s3_key. Runs ONCE per song at upload time.

    Args:
        song_id: the song's ID
        user_id: the user's ID
        art_url: Spotify artwork URL

    Returns:
        List of 3 hex color strings (e.g. ["#1a2b3c", "#4d5e6f", "#7a8b9c"])
    """
    # Download artwork from Spotify
    response = requests.get(art_url, timeout=30)
    response.raise_for_status()
    image = Image.open(BytesIO(response.content)).convert("RGB")

    # Extract 3 dominant colors via quantization
    small = image.resize((150, 150), Image.Resampling.LANCZOS)
    quantized = small.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()

    # Palette is flat [R, G, B, R, G, B, ...] — take top 3
    colors = []
    for i in range(0, min(24, len(palette)), 3):
        r, g, b = palette[i], palette[i + 1], palette[i + 2]
        colors.append(f"#{r:02x}{g:02x}{b:02x}")
        if len(colors) == 3:
            break

    # Cache artwork to S3
    artwork_s3_key = f"artwork/{song_id}.jpg"
    try:
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=90)
        buffer.seek(0)

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=artwork_s3_key,
            Body=buffer,
            ContentType="image/jpeg",
        )
        logger.info(f"Cached artwork: s3://{S3_BUCKET}/{artwork_s3_key}")
    except Exception as e:
        logger.error(f"Artwork cache failed: {e}")
        raise

    # Update song record in DynamoDB
    songs_table = dynamodb.Table("noisemaker-songs")
    try:
        songs_table.update_item(
            Key={"user_id": user_id, "song_id": song_id},
            UpdateExpression="SET color_palette = :cp, cached_artwork_s3_key = :key",
            ExpressionAttributeValues={
                ":cp": colors,
                ":key": artwork_s3_key,
            },
        )
        logger.info(f"Updated song {song_id} with color palette: {colors}")
    except Exception as e:
        logger.error(f"Song record update failed: {e}")
        raise

    return colors


def check_content_available(
    user_id: str, song_id: str, platform: str, song_count: int
) -> dict | None:
    """
    Check if reusable content exists for this song + platform combination.
    Returns the oldest active content (FIFO) that hasn't hit its post limit.

    Reuse rules:
        3-song mode (song_count == 3): reusable if posted_to[platform] < 1
        1 or 2-song mode:              reusable if posted_to[platform] < 2

    Returns:
        Content dict if reusable, None if new generation needed.
    """
    max_posts = 1 if song_count == 3 else 2

    table = dynamodb.Table("noisemaker-content")
    try:
        response = table.query(
            KeyConditionExpression=Key("user_id").eq(user_id),
            FilterExpression=Attr("song_id").eq(song_id) & Attr("status").eq("active"),
        )
    except Exception as e:
        logger.error(f"Content query failed: {e}")
        return None

    items = response.get("Items", [])
    if not items:
        return None

    # FIFO — oldest first
    items.sort(key=lambda x: x.get("created_at", ""))

    for item in items:
        posted_to = item.get("posted_to", {})
        platform_posts = int(posted_to.get(platform, 0))
        if platform_posts < max_posts:
            return item

    return None
