"""
NOiSEMaKER Content Generator
=============================

Generates platform-specific promotional images for user songs.

Process:
1. Generate an abstract background via HuggingFace Inference API (FLUX.1-schnell)
2. Composite the song's Spotify album artwork centered on the background (~60% canvas)
3. Add text overlay with song name and artist name
4. Upload final image to S3 and record in DynamoDB

Uses the same art style and artist rotation lists as frank_art_generator.py,
but replaces the color system with song-specific color palettes (3 hex colors
extracted from each song's Spotify artwork).

Content reuse rules:
    - 1 or 2-song mode: content can be posted TWICE to same platform before regeneration
    - 3-song mode: content can be posted ONCE per platform before regeneration

Extended promo songs ($10/month) are NOT handled here — they have a separate
3-day rotation system.
"""

import os
import uuid
import time
import logging
from datetime import datetime, timezone
from io import BytesIO
from typing import Optional

import boto3
import requests
from boto3.dynamodb.conditions import Key, Attr
from PIL import Image, ImageDraw, ImageFont
from content.caption_generator import generate_caption

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
S3_BUCKET = os.environ.get("S3_BUCKET", "noisemakerpromobydoowopp")

# Platform image dimensions (width, height)
# None = video platform — image generation skipped (Phase 2)
PLATFORM_SIZES = {
    "instagram": (1080, 1080),
    "twitter": (1200, 675),
    "facebook": (1200, 630),
    "threads": (1080, 1080),
    "reddit": (1200, 630),
    "discord": (1200, 675),
    "tiktok": None,
    "youtube": None,
}

# =============================================================================
# ROTATING LISTS (copied from frank_art_generator.py)
# =============================================================================

ART_STYLES = [
    "Abstract geometric",
    "Cubism",
    "Surrealism",
    "Art Deco",
    "Minimalist",
    "Abstract Expressionism",
    "Vaporwave",
]

ARTIST_STYLES = [
    "Jean-Michel Basquiat",
    "Georges Braque",
    "Mark Rothko",
    "Ernst Ludwig Kirchner",
    "Malgorzata Kmiec",
    "Pascal Blanche",
    "Kazimir Malevich",
    "Yayoi Kusama",
    "Willem de Kooning",
    "Finn Campbell-Norman",
    "Elena Kotliarker",
]

# =============================================================================
# AWS CLIENTS
# =============================================================================

s3_client = boto3.client("s3", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
ssm_client = boto3.client("ssm", region_name=AWS_REGION)

HF_TOKEN = ssm_client.get_parameter(
    Name="/noisemaker/huggingface_token",
    WithDecryption=True,
)["Parameter"]["Value"]


# =============================================================================
# IMAGE GENERATION (INTERNAL)
# =============================================================================

def _generate_background(
    prompt: str, size: tuple[int, int], retry_count: int = 2
) -> Optional[Image.Image]:
    """
    Generate background image via HuggingFace Inference API (FLUX.1-schnell).
    Same model and retry logic as frank_art_generator.py.
    """
    try:
        from huggingface_hub import InferenceClient

        logger.info(f"Generating background: {prompt[:80]}...")

        client = InferenceClient(api_key=HF_TOKEN)
        image = client.text_to_image(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell",
        )

        if image.size != size:
            image = image.resize(size, Image.Resampling.LANCZOS)

        logger.info(f"Background generated: {image.size}")
        return image

    except Exception as e:
        error_msg = str(e).lower()

        if retry_count > 0 and any(
            k in error_msg for k in ("queue", "timeout", "503", "429")
        ):
            logger.warning(f"Retrying in 30s... ({retry_count} retries left)")
            time.sleep(30)
            return _generate_background(prompt, size, retry_count - 1)

        logger.error(f"Background generation failed: {e}")
        return None


def _download_artwork_from_s3(s3_key: str) -> Optional[Image.Image]:
    """Download cached song artwork from S3."""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        image_data = response["Body"].read()
        return Image.open(BytesIO(image_data)).convert("RGBA")
    except Exception as e:
        logger.error(f"Failed to download artwork from S3: {e}")
        return None


def _composite_image(
    background: Image.Image,
    artwork: Image.Image,
    song_name: str,
    artist_name: str,
) -> Image.Image:
    """Layer artwork centered on background at ~60% of canvas, add text overlay."""
    bg = background.convert("RGBA")
    bg_w, bg_h = bg.size

    # Resize artwork to ~60% of the smaller canvas dimension
    target_size = int(min(bg_w, bg_h) * 0.6)
    artwork = artwork.resize((target_size, target_size), Image.Resampling.LANCZOS)

    # Center artwork on background
    x = (bg_w - target_size) // 2
    y = (bg_h - target_size) // 2
    bg.paste(artwork, (x, y), artwork)

    # Text overlay
    draw = ImageDraw.Draw(bg)

    try:
        font_large = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            int(bg_h * 0.04),
        )
        font_small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            int(bg_h * 0.03),
        )
    except OSError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Song name centered below artwork
    text_y = y + target_size + int(bg_h * 0.03)
    song_bbox = draw.textbbox((0, 0), song_name, font=font_large)
    song_w = song_bbox[2] - song_bbox[0]
    draw.text(
        ((bg_w - song_w) // 2, text_y),
        song_name,
        fill="white",
        font=font_large,
        stroke_width=2,
        stroke_fill="black",
    )

    # Artist name centered below song name
    artist_y = text_y + int(bg_h * 0.05)
    artist_bbox = draw.textbbox((0, 0), artist_name, font=font_small)
    artist_w = artist_bbox[2] - artist_bbox[0]
    draw.text(
        ((bg_w - artist_w) // 2, artist_y),
        artist_name,
        fill="white",
        font=font_small,
        stroke_width=1,
        stroke_fill="black",
    )

    return bg.convert("RGB")


# =============================================================================
# PUBLIC API
# =============================================================================

def generate_content(song_data: dict, platform: str, user_id: str, song_count: int = 3) -> dict:
    """
    Generate a promotional image for a song on a specific platform.

    Args:
        song_data: dict with song_id, song_name, artist_name, genre,
                   color_palette (list of 3 hex strings), cached_artwork_s3_key
        platform: target platform name
        user_id: the user's ID

    Returns:
        dict with content_id, image_s3_key, caption.
        Empty dict if platform is video-only or generation fails.
    """
    size = PLATFORM_SIZES.get(platform)
    if size is None:
        logger.info(f"Skipping {platform} — video platform (Phase 2)")
        return {}

    content_id = str(uuid.uuid4())

    # Pick art style and artist — deterministic variety from content_id
    uid_int = uuid.UUID(content_id).int
    art_style = ART_STYLES[uid_int % len(ART_STYLES)]
    artist = ARTIST_STYLES[uid_int % len(ARTIST_STYLES)]

    # Build prompt using song's color palette
    color_str = ", ".join(song_data["color_palette"])
    prompt = (
        f"create a {art_style} background graphic "
        f"in the style of {artist} using {color_str}"
    )

    # Generate background
    background = _generate_background(prompt, size)
    if background is None:
        return {}

    # Download cached artwork from S3
    artwork = _download_artwork_from_s3(song_data["cached_artwork_s3_key"])
    if artwork is None:
        return {}

    # Composite background + artwork + text
    final_image = _composite_image(
        background, artwork, song_data["song_name"], song_data["artist_name"]
    )

    # Generate caption
    caption = generate_caption(
        song_data["song_name"],
        song_data["artist_name"],
        song_data.get("genre", "Music"),
        platform,
    )

    # Upload to S3 as JPEG
    s3_key = f"content/{user_id}/{content_id}.jpg"
    try:
        buffer = BytesIO()
        final_image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=buffer,
            ContentType="image/jpeg",
        )
        logger.info(f"Uploaded content: s3://{S3_BUCKET}/{s3_key}")
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")
        return {}

    # Store record in DynamoDB
    table = dynamodb.Table("noisemaker-content")
    try:
        table.put_item(Item={
            "user_id": user_id,
            "content_id": content_id,
            "song_id": song_data["song_id"],
            "image_s3_key": s3_key,
            "platform": platform,
            "caption": caption,
            "color_palette": song_data["color_palette"],
            "song_count": song_count,
            "posted_to": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
        })
        logger.info(f"Content record stored: {content_id}")
    except Exception as e:
        logger.error(f"DynamoDB write failed: {e}")
        return {}

    return {
        "content_id": content_id,
        "image_s3_key": s3_key,
        "caption": caption,
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
